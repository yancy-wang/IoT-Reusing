import SwiftUI

@main
struct Thunderboard_APPApp: App {
    var body: some Scene {
        WindowGroup {
            ViewControllerWrapper() // 用 SwiftUI 包装 UIKit 的 ViewController
        }
    }
}
