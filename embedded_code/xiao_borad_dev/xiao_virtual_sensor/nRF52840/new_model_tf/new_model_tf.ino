#include <Wire.h>
#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <Arduino.h>
#include "model.h" // 替换为您的 CO 标签预测模型的头文件

// TensorFlow Lite 相关全局变量
tflite::MicroErrorReporter tflErrorReporter;
tflite::AllOpsResolver tflOpsResolver;
const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// TensorFlow Lite 内存分配
constexpr int tensorArenaSize = 8 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));

// 标准化参数
const float mean_eCO2 = 400.0;  // 替换为您的标准化均值
const float scale_eCO2 = 200.0; // 替换为您的标准化缩放因子

// 标签映射数组
const char* CO_LABELS[] = {
    "Low",    // 标签 0
    "Medium", // 标签 1
    "High"    // 标签 2
};
#define NUM_CO_LABELS (sizeof(CO_LABELS) / sizeof(CO_LABELS[0]))

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("Starting CO Label Prediction...");

  // 加载 TensorFlow Lite 模型
  tflModel = tflite::GetModel(model); // `model` 是模型数组
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    while (1);
  }

  // 初始化解释器
  tflInterpreter = new tflite::MicroInterpreter(
      tflModel, tflOpsResolver, tensorArena, tensorArenaSize, &tflErrorReporter);

  // 分配张量所需内存
  TfLiteStatus allocate_status = tflInterpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    Serial.println("AllocateTensors() failed");
    while (1);
  }

  // 获取输入和输出张量
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);
}

void loop() {
  if (Serial.available() > 0) {
    // 从串口读取 eCO2 数据
    String eCO2_str = Serial.readStringUntil('\n');
    eCO2_str.trim(); // 去除空白字符
    float eCO2 = eCO2_str.toFloat();

    if (eCO2 == 0.0 && eCO2_str != "0") {
      Serial.println("ERROR: Invalid eCO2 value received.");
      return;
    }

    // 数据标准化
    float normalized_eCO2 = (eCO2 - mean_eCO2) / scale_eCO2;

    // 将标准化后的值加载到模型输入张量
    tflInputTensor->data.f[0] = normalized_eCO2;

    // 执行模型推理
    TfLiteStatus invokeStatus = tflInterpreter->Invoke();
    if (invokeStatus != kTfLiteOk) {
      Serial.println("ERROR: Model inference failed.");
      return;
    }

    // 获取输出结果并预测标签
    float maxProbability = 0;
    int predictedLabelIndex = -1;

    for (int i = 0; i < NUM_CO_LABELS; i++) {
      float probability = tflOutputTensor->data.f[i];
      if (probability > maxProbability) {
        maxProbability = probability;
        predictedLabelIndex = i;
      }
    }

    // 输出预测结果
    if (predictedLabelIndex >= 0) {
      Serial.print("Predicted Label: ");
      Serial.print(predictedLabelIndex);
      Serial.print(", Inference Time: ");
      Serial.println(millis()); // 输出推理时间（毫秒）
    } else {
      Serial.println("ERROR: Prediction failed.");
    }
  }
}