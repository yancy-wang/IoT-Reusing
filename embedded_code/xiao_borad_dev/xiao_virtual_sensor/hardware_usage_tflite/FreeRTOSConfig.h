#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#include "esp_timer.h" // 用于运行时统计的计时器

// 核心定义
#define configNUM_CORES 1 // ESP32-C3 是单核处理器

// FreeRTOS 基础配置
#define configUSE_PREEMPTION 1
#define configUSE_IDLE_HOOK 1 // 启用空闲任务钩子
#define configUSE_TICK_HOOK 0
#define configCPU_CLOCK_HZ (80000000UL) // CPU 时钟频率
#define configTICK_RATE_HZ ((TickType_t)1000) // 每秒的 FreeRTOS tick 数
#define configMAX_PRIORITIES (5) // 最大任务优先级数
#define configMINIMAL_STACK_SIZE ((unsigned short)512) // 最小任务栈大小
#define configTOTAL_HEAP_SIZE ((size_t)(40 * 1024)) // 总堆大小，调整为 40 KB
#define configMAX_TASK_NAME_LEN (16) // 最大任务名称长度
#define configUSE_TRACE_FACILITY 1 // 启用任务跟踪功能
#define configUSE_16_BIT_TICKS 0 // 使用 32 位 tick
#define configIDLE_SHOULD_YIELD 1
#define configUSE_MUTEXES 1
#define configQUEUE_REGISTRY_SIZE 10
#define configCHECK_FOR_STACK_OVERFLOW 2 // 检查栈溢出
#define configUSE_RECURSIVE_MUTEXES 1
#define configUSE_MALLOC_FAILED_HOOK 1
#define configUSE_APPLICATION_TASK_TAG 0
#define configUSE_COUNTING_SEMAPHORES 1

// 运行时统计相关宏
#define configGENERATE_RUN_TIME_STATS 1 // 启用运行时统计
#define portCONFIGURE_TIMER_FOR_RUN_TIME_STATS() // 使用默认配置
#define portGET_RUN_TIME_COUNTER_VALUE() esp_timer_get_time() // 使用 ESP-IDF 提供的 esp_timer

// 内存分配配置
#define configSUPPORT_DYNAMIC_ALLOCATION 1
#define configSUPPORT_STATIC_ALLOCATION 0

// 任务通知配置
#define configUSE_TASK_NOTIFICATIONS 1
#define configTASK_NOTIFICATION_ARRAY_ENTRIES 1

// 挂起和恢复任务
#define configUSE_TASK_SUSPEND 1

// 时间片轮转
#define configUSE_TIME_SLICING 1

// 调试和跟踪
#define configUSE_STATS_FORMATTING_FUNCTIONS 1
#define configRECORD_STACK_HIGH_ADDRESS 1

// 软件定时器配置
#define configUSE_TIMERS 1
#define configTIMER_TASK_PRIORITY (configMAX_PRIORITIES - 1)
#define configTIMER_QUEUE_LENGTH 10
#define configTIMER_TASK_STACK_DEPTH (configMINIMAL_STACK_SIZE * 2)

// 中断配置
#define configKERNEL_INTERRUPT_PRIORITY 1
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 10

// 断言配置
#define configASSERT(x) if ((x) == 0) { taskDISABLE_INTERRUPTS(); for (;;); }

// FreeRTOS 钩子函数配置
#define configUSE_IDLE_HOOK 1
#define configUSE_TICK_HOOK 0

// 禁用调试任务清理
#define INCLUDE_vTaskDelete 1
#define INCLUDE_vTaskDelay 1
#define INCLUDE_vTaskDelayUntil 1
#define INCLUDE_uxTaskPriorityGet 1
#define INCLUDE_vTaskSuspend 1
#define INCLUDE_xResumeFromISR 1
#define INCLUDE_xTaskGetSchedulerState 1
#define INCLUDE_xTaskGetCurrentTaskHandle 1
#define INCLUDE_xTaskGetIdleTaskHandle 1
#define INCLUDE_xTaskAbortDelay 1
#define INCLUDE_xQueueGetMutexHolder 1
#define INCLUDE_uxTaskGetStackHighWaterMark 1
#define INCLUDE_eTaskGetState 1
#define INCLUDE_vTaskGetIdleRunTimeCounter 1 // 启用空闲任务运行时间统计

#endif /* FREERTOS_CONFIG_H */