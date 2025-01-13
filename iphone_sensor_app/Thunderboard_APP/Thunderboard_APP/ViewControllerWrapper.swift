//
//  ViewControllerWrapper.swift
//  Thunderboard_APP
//
//  Created by 王阳洋 on 2024/11/6.
//

import Foundation
import SwiftUI
import UIKit

struct ViewControllerWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> ViewController {
        return ViewController() // 使用您自定义的 ViewController
    }

    func updateUIViewController(_ uiViewController: ViewController, context: Context) {
        // 在这里更新 ViewController 的 UI 或数据
    }
}
