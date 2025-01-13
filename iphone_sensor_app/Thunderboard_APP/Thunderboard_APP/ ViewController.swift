import Foundation
import UIKit
import CoreBluetooth

class ViewController: UIViewController, CBCentralManagerDelegate, CBPeripheralDelegate {
    var centralManager: CBCentralManager!
    var thunderboardPeripheral: CBPeripheral?
    
    // 定义服务和特征 UUID
    let environmentalSensingServiceUUID = CBUUID(string: "0000181a-0000-1000-8000-00805f9b34fb")
    let temperatureCharacteristicUUID = CBUUID(string: "2A6E")
    
    var readTimer: Timer?
    var requestTimestamps: [CBUUID: Date] = [:]
    var latencyResults: [Double] = []  // 保存每次延时
    var readCount = 0  // 读取计数
    let maxReadCount = 3 // 最大读取次数
    
    override func viewDidLoad() {
        super.viewDidLoad()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == .poweredOn {
            central.scanForPeripherals(withServices: nil, options: nil)
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        if peripheral.name == "Thunder Sense #3389" {
            central.stopScan()
            thunderboardPeripheral = peripheral
            thunderboardPeripheral?.delegate = self
            central.connect(peripheral, options: nil)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheral.discoverServices([environmentalSensingServiceUUID])
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let services = peripheral.services {
            for service in services {
                if service.uuid == environmentalSensingServiceUUID {
                    peripheral.discoverCharacteristics([temperatureCharacteristicUUID], for: service)
                }
            }
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let characteristics = service.characteristics {
            readTimer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
                guard let self = self else { return }
                if self.readCount >= self.maxReadCount {
                    self.readTimer?.invalidate()  // 停止计时器
                    self.saveCSVToDocuments()  // 保存数据到CSV
                    return
                }
                
                for characteristic in characteristics {
                    self.requestTimestamps[characteristic.uuid] = Date()  // 记录请求时间
                    peripheral.readValue(for: characteristic)
                }
                self.readCount += 1
            }
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        let responseTimestamp = Date()
        if let requestTimestamp = requestTimestamps[characteristic.uuid] {
            let latency = responseTimestamp.timeIntervalSince(requestTimestamp) * 1000  // 转换为毫秒
            latencyResults.append(latency)  // 保存延时
            print("Latency for \(characteristic.uuid): \(latency) ms")
        }
    }

    func parseTemperatureData(_ data: Data) -> Float {
        guard data.count >= 2 else { return 0.0 }
        let rawValue = Int(data[1]) << 8 | Int(data[0])
        return Float(rawValue) / 100.0
    }
    
    // 保存延时数据到 CSV 文件到 Documents 文件夹
    func saveCSVToDocuments() {
        let fileName = "latency_results.csv"
        let path = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent(fileName)
        
        var csvText = "Read Count,Latency (ms)\n"
        for (index, latency) in latencyResults.enumerated() {
            csvText += "\(index + 1),\(latency)\n"
        }
        
        do {
            try csvText.write(to: path, atomically: true, encoding: .utf8)
            print("CSV file saved to Documents folder: \(path)")
        } catch {
            print("Failed to write CSV file: \(error)")
        }
    }
}
