################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk/platform/driver/i2cspm/src/sl_i2cspm.c 

OBJS += \
./gecko_sdk_4.4.3/platform/driver/i2cspm/src/sl_i2cspm.o 

C_DEPS += \
./gecko_sdk_4.4.3/platform/driver/i2cspm/src/sl_i2cspm.d 


# Each subdirectory must supply rules for building sources it contributes
gecko_sdk_4.4.3/platform/driver/i2cspm/src/sl_i2cspm.o: /Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk/platform/driver/i2cspm/src/sl_i2cspm.c gecko_sdk_4.4.3/platform/driver/i2cspm/src/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: GNU ARM C Compiler'
	arm-none-eabi-gcc -g -gdwarf-2 -mcpu=cortex-m4 -mthumb -std=c99 '-DEFR32MG12P332F1024GL125=1' '-DSL_APP_PROPERTIES=1' '-DHARDWARE_BOARD_DEFAULT_RF_BAND_2400=1' '-DHARDWARE_BOARD_SUPPORTS_1_RF_BAND=1' '-DHARDWARE_BOARD_SUPPORTS_RF_BAND_2400=1' '-DHFXO_FREQ=38400000' '-DSL_BOARD_NAME="BRD4166A"' '-DSL_BOARD_REV="D03"' '-DSL_COMPONENT_CATALOG_PRESENT=1' '-DMBEDTLS_CONFIG_FILE=<sl_mbedtls_config.h>' '-DMBEDTLS_PSA_CRYPTO_CLIENT=1' '-DMBEDTLS_PSA_CRYPTO_CONFIG_FILE=<psa_crypto_config.h>' '-DSL_RAIL_LIB_MULTIPROTOCOL_SUPPORT=0' '-DSL_RAIL_UTIL_PA_CONFIG_HEADER=<sl_rail_util_pa_config.h>' '-DBRD4166A_SUPPORT=1' -I"/Users/wangyangyang/SimplicityStudio/v5_workspace/bt_soc_thunderboard_brd4166a_ble/config" -I"/Users/wangyangyang/SimplicityStudio/v5_workspace/bt_soc_thunderboard_brd4166a_ble/config/btconf" -I"/Users/wangyangyang/SimplicityStudio/v5_workspace/bt_soc_thunderboard_brd4166a_ble/autogen" -I"/Users/wangyangyang/SimplicityStudio/v5_workspace/bt_soc_thunderboard_brd4166a_ble" -I"/Users/wangyangyang/SimplicityStudio/v5_workspace/bt_soc_thunderboard_brd4166a_ble/brd4166a" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/Device/SiliconLabs/EFR32MG12P/Include" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/common/util/app_assert" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/common/util/app_log" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/common/util/app_timer" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//protocol/bluetooth/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/common/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//protocol/bluetooth/bgcommon/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//protocol/bluetooth/bgstack/ll/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/bmp280/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/bmp280/bosch/BMP280_driver" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/board/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/bootloader" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/bootloader/api" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/driver/button/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/ccs811/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/ccs811/firmware" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/CMSIS/Core/Include" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/configuration_over_swo/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/driver/debug/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/device_init/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/emdrv/dmadrv/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/emdrv/common/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/emlib/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_aio" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_battery" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_device_information" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_gas" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_hall" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_imu" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_light" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_pressure" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_rgb" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_rht" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/gatt_service_sound" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/emdrv/gpiointerrupt/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/driver/i2cspm/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/icm20648/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/imu/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/in_place_ota_dfu" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/iostream/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/driver/leddrv/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/security/sl_component/sl_mbedtls_support/config" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/security/sl_component/sl_mbedtls_support/config/preset" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/security/sl_component/sl_mbedtls_support/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//util/third_party/mbedtls/include" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//util/third_party/mbedtls/library" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/mic/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/mpu/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/mx25_flash_shutdown/inc/sl_mx25_flash_shutdown_usart" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/power_manager/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/power_supply" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/pressure/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//util/third_party/printf" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//util/third_party/printf/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/security/sl_component/sl_psa_driver/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/common" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/protocol/ble" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/protocol/ieee802154" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/protocol/wmbus" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/protocol/zwave" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/chip/efr32/efr32xg1x" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/protocol/sidewalk" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/plugin/pa-conversions" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/plugin/pa-conversions/efr32xg1x" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/plugin/rail_util_power_manager_init" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/radio/rail_lib/plugin/rail_util_pti" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_gas" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_hall" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_imu" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_light" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_pressure" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_rht" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_select" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//app/bluetooth/common/sensor_sound" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/si1133/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/si70xx/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//hardware/driver/si7210/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//util/silicon_labs/silabs_core/memory_manager" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/common/toolchain/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/system/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/sleeptimer/inc" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/security/sl_component/sl_protocol_crypto/src" -I"/Users/wangyangyang/SimplicityStudio/SDKs/gecko_sdk//platform/service/udelay/inc" -Os -Wall -Wextra -ffunction-sections -fdata-sections -imacrossl_gcc_preinclude.h -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -fno-builtin-printf -fno-builtin-sprintf --specs=nano.specs -c -fmessage-length=0 -MMD -MP -MF"gecko_sdk_4.4.3/platform/driver/i2cspm/src/sl_i2cspm.d" -MT"$@" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


