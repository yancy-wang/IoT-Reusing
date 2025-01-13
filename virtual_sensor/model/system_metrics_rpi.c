#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void get_memory_info() {
    FILE *fp = fopen("/proc/meminfo", "r");
    if (fp == NULL) {
        perror("Failed to read /proc/meminfo");
        return;
    }
    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        printf("%s", line);
    }
    fclose(fp);
}

void get_cpu_temperature() {
    FILE *fp = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (fp == NULL) {
        perror("Failed to read CPU temperature");
        return;
    }
    char temp[10];
    fgets(temp, sizeof(temp), fp);
    printf("CPU Temperature: %.2fC\n", atof(temp) / 1000.0);
    fclose(fp);
}

void get_cpu_usage() {
    FILE *fp = fopen("/proc/stat", "r");
    if (fp == NULL) {
        perror("Failed to read /proc/stat");
        return;
    }

    unsigned long long user, nice, system, idle, iowait, irq, softirq, total_time, idle_time;

    // 读取第一行（即 CPU 时间统计）
    fscanf(fp, "cpu %llu %llu %llu %llu %llu %llu %llu %llu", 
           &user, &nice, &system, &idle, &iowait, &irq, &softirq, &total_time);
    fclose(fp);

    // 计算总时间和空闲时间
    total_time = user + nice + system + idle + iowait + irq + softirq;
    idle_time = idle + iowait;

    // 计算 CPU 使用率
    static unsigned long long last_total_time = 0, last_idle_time = 0;
    unsigned long long total_diff = total_time - last_total_time;
    unsigned long long idle_diff = idle_time - last_idle_time;

    double cpu_usage = (total_diff - idle_diff) * 100.0 / total_diff;

    // 保存当前时间
    last_total_time = total_time;
    last_idle_time = idle_time;

    printf("CPU Usage: %.2f%%\n", cpu_usage);
}

int main() {
    get_memory_info();
    get_cpu_temperature();
    get_cpu_usage();
    return 0;
}