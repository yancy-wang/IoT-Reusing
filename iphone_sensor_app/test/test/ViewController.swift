import Foundation
import UIKit
import CoreBluetooth
import MessageUI

class ViewController: UIViewController, CBCentralManagerDelegate, CBPeripheralDelegate, MFMailComposeViewControllerDelegate {

    var centralManager: CBCentralManager!
    var thunderboardPeripheral: CBPeripheral?

    // 定义服务和特征 UUID
    let environmentalSensingServiceUUID = CBUUID(string: "0000181a-0000-1000-8000-00805f9b34fb")
    let temperatureCharacteristicUUID = CBUUID(string: "2A6E")

    var requestTimestamps: [CBUUID: Date] = [:]
    var bluetoothLatencies: [Double] = []  // 记录蓝牙延时
    var networkLatencies: [Double] = []    // 记录网络延时
    var readCount = 0                      // 当前读取次数
    let maxReadCount = 1000                // 最大读取次数
    var timer: Timer?                      // 用于控制读取的定时器

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
        if peripheral.name == "Thunder Sense #5442" {
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
            timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
                guard let self = self else { return }

                if self.readCount >= self.maxReadCount {
                    self.timer?.invalidate()  // 停止计时器
                    self.saveAndEmailCSV()  // 完成数据并保存和发送 CSV 文件
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
            let bluetoothLatency = responseTimestamp.timeIntervalSince(requestTimestamp) * 1000  // 转换为毫秒
            bluetoothLatencies.append(bluetoothLatency)  // 保存蓝牙延时
            print("Bluetooth latency for \(characteristic.uuid): \(bluetoothLatency) ms")

            // 检查是否是温度特征并发送至服务器
            if characteristic.uuid == temperatureCharacteristicUUID, let data = characteristic.value {
                let temperature = parseTemperatureData(data)
                sendTemperatureToServer(temperature: temperature) // 发送温度数据到服务器
            }
        }
    }

    func parseTemperatureData(_ data: Data) -> Float {
        guard data.count >= 2 else { return 0.0 }
        let rawValue = Int(data[1]) << 8 | Int(data[0])
        return Float(rawValue) / 100.0
    }

    // 使用 HTTP 发送温度数据
    func sendTemperatureToServer(temperature: Float) {
        let url = URL(string: "http://195.148.30.41:5000/sensor")!  // 修改为你的服务器 URL
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let postData: [String: Any] = [
            "temperature": temperature,
            "timestamp": Date().timeIntervalSince1970
        ]

        do {
            let jsonData = try JSONSerialization.data(withJSONObject: postData, options: [])
            request.httpBody = jsonData

            let session = URLSession(configuration: .default)
            let taskStartTime = Date()  // 记录发送请求的时间
            let task = session.dataTask(with: request) { data, response, error in
                let taskEndTime = Date()  // 记录请求完成的时间
                let networkLatency = taskEndTime.timeIntervalSince(taskStartTime) * 1000  // 转换为毫秒
                self.networkLatencies.append(networkLatency)

                if let error = error {
                    print("HTTP 请求失败: \(error.localizedDescription)")
                    return
                }

                if let httpResponse = response as? HTTPURLResponse {
                    print("HTTP 响应状态码: \(httpResponse.statusCode)")
                    print("网络延时: \(networkLatency) ms")
                }
            }
            task.resume()
        } catch {
            print("JSON 序列化失败: \(error.localizedDescription)")
        }
    }

    // 保存延时数据到 CSV 文件到 Documents 文件夹并通过邮件发送
    func saveAndEmailCSV() {
        let fileName = "latency_results.csv"
        let path = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent(fileName)

        var csvText = "Read Count,Bluetooth Latency (ms),Network Latency (ms)\n"
        for i in 0..<bluetoothLatencies.count {
            let bluetoothLatency = bluetoothLatencies[i]
            let networkLatency = i < networkLatencies.count ? networkLatencies[i] : 0.0
            csvText += "\(i + 1),\(bluetoothLatency),\(networkLatency)\n"
        }

        do {
            try csvText.write(to: path, atomically: true, encoding: .utf8)
            print("CSV file saved at: \(path)")
            sendCSVViaEmail(fileURL: path)
        } catch {
            print("Failed to write CSV file: \(error)")
        }
    }

    // 使用邮件发送 CSV 文件
    func sendCSVViaEmail(fileURL: URL) {
        if MFMailComposeViewController.canSendMail() {
            if presentedViewController == nil {  // 检查是否已有邮件视图控制器在显示
                let mail = MFMailComposeViewController()
                mail.mailComposeDelegate = self
                mail.setSubject("Latency Results CSV")
                mail.setMessageBody("请查收附件中的延时数据", isHTML: false)
                if let fileData = try? Data(contentsOf: fileURL) {
                    mail.addAttachmentData(fileData, mimeType: "text/csv", fileName: "latency_results.csv")
                }
                present(mail, animated: true)
            }
        } else {
            print("无法发送邮件，请检查邮件配置")
        }
    }

    // 处理邮件发送结果
    func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
        controller.dismiss(animated: true)
        switch result {
        case .sent:
            print("邮件发送成功")
        case .saved:
            print("邮件已保存为草稿")
        case .cancelled:
            print("邮件已取消")
        case .failed:
            print("邮件发送失败: \(String(describing: error))")
        @unknown default:
            break
        }
    }
}
