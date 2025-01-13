#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#include "model.h"  // TensorFlow Lite 模型头文件
#include "esp_heap_caps.h"  // 用于检查内存使用情况
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_log.h"

// TensorFlow Lite Globals
namespace {
const tflite::Model *model = nullptr;
tflite::MicroInterpreter *interpreter = nullptr;
TfLiteTensor *input = nullptr;
TfLiteTensor *output = nullptr;

constexpr int kTensorArenaSize = 2048;
uint8_t tensor_arena[kTensorArenaSize];
}  // namespace

unsigned long total_inference_time = 0;  // 总推理时间
int data_points_processed = 0;           // 已处理的数据点数

#define LOG_TAG "TFLITE_CPU_MEM"

// 函数：打印内存使用
void printMemoryUsage(const char *tag) {
  size_t free_heap = heap_caps_get_free_size(MALLOC_CAP_DEFAULT);
  size_t free_internal = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
  size_t free_spiram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  Serial.printf("[%s] Free Heap: %d bytes, Internal RAM: %d bytes, SPI RAM: %d bytes\n",
                tag, free_heap, free_internal, free_spiram);
}

// 函数：打印 Tensor Arena 使用情况
void printArenaUsage(const char *tag) {
  if (interpreter) {
    size_t used_bytes = interpreter->arena_used_bytes();
    Serial.printf("[%s] Tensor Arena Used: %d bytes, Total Tensor Arena Size: %d bytes\n",
                  tag, used_bytes, kTensorArenaSize);
    Serial.printf("[%s] Tensor Arena Free: %d bytes\n",
                  tag, kTensorArenaSize - used_bytes);
  } else {
    Serial.printf("[%s] Tensor Arena not initialized.\n", tag);
  }
}

// 函数：计算 CPU 使用率
void logCpuUsage() {
  static uint32_t last_idle_time = 0;
  static uint32_t last_total_time = 0;

  // 获取当前空闲时间和总时间
  uint32_t current_idle_time = xTaskGetIdleRunTimeCounter();
  uint32_t current_total_time = xTaskGetTickCount() * portTICK_PERIOD_MS;

  // 计算时间差
  uint32_t idle_time_diff = current_idle_time - last_idle_time;
  uint32_t total_time_diff = current_total_time - last_total_time;

  // 计算 CPU 使用率
  if (total_time_diff > 0) {
    float cpu_usage = 100.0f * (1.0f - ((float)idle_time_diff / total_time_diff));
    Serial.printf("[CPU Usage] CPU Usage: %.2f%%\n", cpu_usage);
  } else {
    Serial.printf("[CPU Usage] Insufficient time difference to calculate CPU usage.\n");
  }

  // 更新记录的时间
  last_idle_time = current_idle_time;
  last_total_time = current_total_time;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) {}

  // 初始化 TensorFlow Lite 模型前的内存检查
  printMemoryUsage("Before TFLite Initialization");

  // 初始化 TensorFlow Lite 模型
  model = tflite::GetModel(g_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    return;
  }

  static tflite::MicroMutableOpResolver<2> resolver;
  resolver.AddFullyConnected();
  resolver.AddSoftmax();

  // 初始化解释器并记录内存占用情况
  static tflite::MicroInterpreter static_interpreter(
      model, resolver, tensor_arena, kTensorArenaSize);
  interpreter = &static_interpreter;

  // 分配张量内存
  if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("AllocateTensors() failed");
    return;
  }

  input = interpreter->input(0);
  output = interpreter->output(0);

  // 初始化 TensorFlow Lite 模型后的内存检查
  printMemoryUsage("After TFLite Initialization");
  printArenaUsage("After TFLite Initialization");

  Serial.println("Setup complete. Ready to receive eCO2 values...");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    if (line.length() > 0) {
      float eCO2_value = line.toFloat();
      Serial.printf("Received eCO2: %.2f\n", eCO2_value);

      // 量化输入数据 (假设 eCO2 范围 400-2000)
      int8_t quantized_eCO2 = eCO2_value / input->params.scale + input->params.zero_point;
      input->data.int8[0] = quantized_eCO2;

      // 记录开始时间
      unsigned long start_time = micros();

      // 推理
      if (interpreter->Invoke() == kTfLiteOk) {
        unsigned long end_time = micros();  // 记录结束时间
        unsigned long inference_time = end_time - start_time;  // 计算推理时间
        total_inference_time += inference_time;  // 累加到总时间
        data_points_processed++;  // 增加数据点计数

        int predicted_label = 0;
        float max_value = output->data.f[0];
        for (int i = 1; i < output->dims->data[1]; i++) {
          if (output->data.f[i] > max_value) {
            max_value = output->data.f[i];
            predicted_label = i;
          }
        }

        // 返回预测结果和推理时间
        Serial.printf("Predicted Label: %d, Inference Time: %lu us\n", predicted_label, inference_time);

        // 如果处理了1000个数据点，计算平均时间
        if (data_points_processed >= 1000) {
          float average_time = (float)total_inference_time / data_points_processed;
          Serial.printf("Processed 1000 data points. Average Inference Time: %.2f us\n", average_time);
          total_inference_time = 0;  // 重置计数
          data_points_processed = 0;
        }

        // 打印推理后的内存状态和 Tensor Arena 使用情况
        printMemoryUsage("After Inference");
        printArenaUsage("After Inference");
      } else {
        Serial.println("ERROR: Inference failed!");
      }
    }
  }

  // 定期打印 CPU 使用率（例如每 5 秒）
  static unsigned long last_log_time = 0;
  if (millis() - last_log_time > 5000) {
    logCpuUsage();
    last_log_time = millis();
  }
}