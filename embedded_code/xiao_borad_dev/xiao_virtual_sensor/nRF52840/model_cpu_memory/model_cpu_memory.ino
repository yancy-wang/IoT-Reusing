#include <Arduino.h>
#include <Wire.h>
#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include "model.h" // Include your CO label prediction model header

// TensorFlow Lite global variables
tflite::MicroErrorReporter tflErrorReporter;
tflite::AllOpsResolver tflOpsResolver;
const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// TensorFlow Lite memory allocation
constexpr int tensorArenaSize = 8 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));

// Normalization parameters
const float mean_eCO2 = 400.0;  // Replace with your standardization mean
const float scale_eCO2 = 200.0; // Replace with your standardization scale

// Label mapping array
const char* CO_LABELS[] = {
    "Low",    // Label 0
    "Medium", // Label 1
    "High"    // Label 2
};
#define NUM_CO_LABELS (sizeof(CO_LABELS) / sizeof(CO_LABELS[0]))

// Function to calculate free memory (stack and heap usage)
int getFreeMemory() {
  extern char _end;      // End of the static memory
  extern char *__HeapLimit;
  char *stackTop = (char *)malloc(4); // Get the current stack pointer
  char *heapTop = (char *)__HeapLimit;
  free(stackTop);
  return stackTop - heapTop;
}

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("Starting CO Label Prediction...");

  // Load TensorFlow Lite model
  tflModel = tflite::GetModel(model); // `model` is the model array
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema mismatch!");
    while (1);
  }

  // Initialize interpreter
  tflInterpreter = new tflite::MicroInterpreter(
      tflModel, tflOpsResolver, tensorArena, tensorArenaSize, &tflErrorReporter);

  // Allocate tensor memory
  TfLiteStatus allocate_status = tflInterpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    Serial.println("AllocateTensors() failed");
    while (1);
  }

  // Get input and output tensors
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);

  Serial.println("Setup complete.");
}

void loop() {
  if (Serial.available() > 0) {
    // Read eCO2 data from the serial input
    String eCO2_str = Serial.readStringUntil('\n');
    eCO2_str.trim(); // Remove whitespace
    float eCO2 = eCO2_str.toFloat();

    if (eCO2 == 0.0 && eCO2_str != "0") {
      Serial.println("ERROR: Invalid eCO2 value received.");
      return;
    }

    // Normalize the eCO2 value
    float normalized_eCO2 = (eCO2 - mean_eCO2) / scale_eCO2;

    // Load normalized value into the model input tensor
    tflInputTensor->data.f[0] = normalized_eCO2;

    // Measure inference time
    unsigned long totalStartTime = micros();
    unsigned long inferenceStartTime = micros();
    TfLiteStatus invokeStatus = tflInterpreter->Invoke();
    unsigned long inferenceEndTime = micros();

    if (invokeStatus != kTfLiteOk) {
      Serial.println("ERROR: Model inference failed.");
      return;
    }

    // Calculate metrics
    unsigned long inferenceTime = inferenceEndTime - inferenceStartTime;
    unsigned long totalEndTime = micros();
    unsigned long totalLoopTime = totalEndTime - totalStartTime;

    // CPU usage is the percentage of time spent in inference
    float cpuUsage = (float(inferenceTime) / float(totalLoopTime)) * 100.0;

    // Get memory usage
    int freeMemoryBytes = getFreeMemory();
    int usedMemoryBytes = tensorArenaSize - freeMemoryBytes;

    // Get output results and predict the label
    float maxProbability = 0;
    int predictedLabelIndex = -1;

    Serial.println("Prediction Probabilities:");
    for (int i = 0; i < NUM_CO_LABELS; i++) {
      float probability = tflOutputTensor->data.f[i];
      Serial.print(CO_LABELS[i]);
      Serial.print(": ");
      Serial.print(probability * 100, 2);
      Serial.println("%");
      if (probability > maxProbability) {
        maxProbability = probability;
        predictedLabelIndex = i;
      }
    }

    if (predictedLabelIndex >= 0) {
      Serial.print("Predicted Label: ");
      Serial.print(predictedLabelIndex);
      Serial.print(" (");
      Serial.print(CO_LABELS[predictedLabelIndex]);
      Serial.print(")");
    } else {
      Serial.println("ERROR: Prediction failed.");
    }

    // Output metrics
    Serial.print(", Inference Time: ");
    Serial.print(inferenceTime);
    Serial.println(" us");

    Serial.print("CPU Usage: ");
    Serial.print(cpuUsage, 2);
    Serial.println(" %");

    Serial.print("Used Memory: ");
    Serial.print(usedMemoryBytes);
    Serial.println(" bytes");

    Serial.print("Free Memory: ");
    Serial.print(freeMemoryBytes);
    Serial.println(" bytes");

    Serial.println();
  }
}