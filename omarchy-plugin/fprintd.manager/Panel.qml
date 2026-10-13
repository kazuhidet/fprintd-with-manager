import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import qs.Commons
import qs.Ui

Item {
    id: root
    property var shell: null
    property var settings: ({})
    property var readers: []
    property var locations: []
    property string selectedDevice: ""
    property string selectedFinger: "right-index-finger"
    property int attempts: 7
    property int timeout: 30
    property string message: "状態を読み込んでいます…"
    property string history: ""
    property real progress: 0
    property string pendingAction: ""
    property string pendingFinger: ""
    property bool gotResult: false
    property bool opened: false
    property bool focusPrimed: false
    property var popupScreen: null
    readonly property bool busy: operation.running || status.running
    readonly property var reader: readers.find(function(r) { return r.path === selectedDevice }) || null
    readonly property var deviceOptions: readers.map(function(r) { return {value: r.path, label: r.name} })
    readonly property var fingerOptions: [
        {value: "right-index-finger", label: "右の人差し指"}, {value: "left-index-finger", label: "左の人差し指"},
        {value: "right-thumb", label: "右の親指"}, {value: "left-thumb", label: "左の親指"},
        {value: "right-middle-finger", label: "右の中指"}, {value: "left-middle-finger", label: "左の中指"},
        {value: "right-ring-finger", label: "右の薬指"}, {value: "left-ring-finger", label: "左の薬指"},
        {value: "right-little-finger", label: "右の小指"}, {value: "left-little-finger", label: "左の小指"}
    ]
    function command(action) {
        return ["/usr/bin/python3", Qt.resolvedUrl("backend.py").toString().replace(/^file:\/\//, ""), action]
    }
    function refresh() {
        if (!busy) { status.command = command("status"); status.running = true }
    }
    function open(payload) {
        var monitor = Hyprland.focusedMonitor
        popupScreen = Quickshell.screens.find(function(s) { return monitor && s.name === monitor.name }) || Quickshell.screens[0]
        focusPrimed = false
        opened = true
        focusPrime.restart()
        Qt.callLater(function() { contentFocus.forceActiveFocus() })
        refresh()
    }
    function close() {
        if (operation.running) operation.signal(15)
        opened = false
        confirmation.opened = false
        focusPrime.stop()
    }
    function requestClose() {
        if (shell) shell.hide("fprintd.manager")
        else close()
    }
    function run(action, finger) {
        if (busy || !reader) return
        var args = command(action).concat(["--device", selectedDevice])
        if (finger) args = args.concat(["--finger", finger])
        start(args)
    }
    function start(args) {
        gotResult = false
        progress = 0
        message = "処理中…"
        operation.command = args
        operation.running = true
    }
    function configure(location, enable) {
        if (busy) return
        start(command("pam").concat(["--location", location, "--enable", enable ? "1" : "0",
                                     "--tries", String(attempts), "--timeout", String(timeout)]))
    }
    function confirm(action, finger) {
        pendingAction = action
        pendingFinger = finger || ""
        confirmation.message = action === "enroll"
            ? "この指は登録済みです。指紋を登録し直しますか？"
            : finger ? "選択した指の指紋を削除しますか？" : "このデバイスの登録済み指紋をすべて削除しますか？"
        confirmation.opened = true
    }
    function receive(line) {
        try {
            var data = JSON.parse(line)
            if (data.type === "state") {
                readers = data.devices
                locations = data.locations
                attempts = data.tries
                timeout = data.timeout
                if (!reader) selectedDevice = readers.length ? readers[0].path : ""
                if (data.error) message = data.error
                else if (!readers.length) message = "fprintd 対応デバイスが見つかりません"
                else if (history === "") message = "指紋を登録・照合できます"
            } else {
                message = data.message
                if (data.type === "progress") progress = data.progress
                if (data.type === "result") { gotResult = true; if (data.success) progress = 1 }
                history = (history + new Date().toLocaleTimeString() + " " + message + "\n").slice(-16000)
            }
        } catch (e) { message = "バックエンド応答を読み取れません: " + line }
    }
    Process {
        id: status
        stdout: SplitParser { onRead: function(line) { root.receive(line) } }
        stderr: StdioCollector { onStreamFinished: if (text) root.message = text }
    }
    Process {
        id: operation
        stdout: SplitParser { onRead: function(line) { root.receive(line) } }
        stderr: StdioCollector { onStreamFinished: if (text) root.message = text }
        onExited: function(code) {
            if (!root.gotResult) root.message = code === 0 ? "完了" : "処理を終了しました（終了コード " + code + "）"
            Qt.callLater(root.refresh)
        }
    }
    Timer {
        id: focusPrime
        interval: 150
        onTriggered: root.focusPrimed = true
    }
    PanelWindow {
        id: window
        visible: root.opened
        screen: root.popupScreen
        anchors { top: true; bottom: true; left: true; right: true }
        color: "transparent"
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: "fprintd-manager"
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: root.opened
            ? (root.focusPrimed ? WlrKeyboardFocus.OnDemand : WlrKeyboardFocus.Exclusive)
            : WlrKeyboardFocus.None
        Rectangle { anchors.fill: parent; color: Color.menu.scrim }
        MouseArea { anchors.fill: parent; onClicked: root.requestClose() }
        BorderSurface {
            anchors.centerIn: parent
            width: Math.min(Style.space(640), Math.max(0, window.width - Style.gapsOut * 2))
            height: Math.min(Style.space(740), Math.max(0, window.height - Style.gapsOut * 2))
            color: Color.background
            radius: Style.cornerRadius
            borderSpec: Border.surfaceSpec("popups", "border", Color.popups.border, Math.max(1, Style.space(2)))
            MouseArea { anchors.fill: parent; onClicked: {} }
            FocusScope {
                id: contentFocus
                anchors.fill: parent
                focus: true
                Keys.onEscapePressed: { if (confirmation.opened) confirmation.opened = false; else root.requestClose() }
                QQC.ScrollView {
                    anchors.fill: parent
                    anchors.margins: Style.space(20)
                    contentWidth: availableWidth
                    ColumnLayout {
                        width: parent.width
                        spacing: Style.space(12)
                        Text { text: "指紋マネージャー"; color: Color.foreground; font.pixelSize: Style.font.title; font.family: Style.font.family }
                        Text { text: root.message; textFormat: Text.PlainText; color: Color.foreground; wrapMode: Text.Wrap; Layout.fillWidth: true }
                        QQC.ProgressBar { from: 0; to: 1; value: root.progress; visible: operation.running; Layout.fillWidth: true }
                        RowLayout {
                            Button { text: "更新"; focusable: true; enabled: !root.busy; onClicked: root.refresh() }
                            Button { text: "キャンセル"; focusable: true; visible: operation.running; onClicked: operation.signal(15) }
                        }
                        Dropdown { label: "デバイス"; options: root.deviceOptions; value: root.selectedDevice; enabled: !root.busy; Layout.fillWidth: true; onChanged: function(value) { root.selectedDevice = value } }
                        Dropdown { label: "登録・照合・削除する指"; options: root.fingerOptions; value: root.selectedFinger; enabled: !root.busy; Layout.fillWidth: true; onChanged: function(value) { root.selectedFinger = value } }
                        Text {
                            text: "登録済み: " + (root.reader && root.reader.fingers.length ? root.reader.fingers.map(function(f) { return (root.fingerOptions.find(function(o) { return o.value === f }) || {label: f}).label }).join("、") : "なし")
                            color: Color.foreground; wrapMode: Text.Wrap; Layout.fillWidth: true
                        }
                        Flow {
                            Layout.fillWidth: true
                            spacing: Style.space(8)
                            Button { text: "登録"; focusable: true; enabled: !root.busy && !!root.reader; onClicked: {
                                if (root.reader.fingers.indexOf(root.selectedFinger) >= 0) root.confirm("enroll", root.selectedFinger)
                                else root.run("enroll", root.selectedFinger)
                            } }
                            Button { text: "選択した指を照合"; focusable: true; enabled: !root.busy && !!root.reader && root.reader.fingers.indexOf(root.selectedFinger) >= 0; onClicked: root.run("verify", root.selectedFinger) }
                            Button { text: "選択した指を削除"; focusable: true; enabled: !root.busy && !!root.reader && root.reader.fingers.indexOf(root.selectedFinger) >= 0; onClicked: root.confirm("delete", root.selectedFinger) }
                            Button { text: "すべて削除"; focusable: true; enabled: !root.busy && !!root.reader && root.reader.fingers.length > 0; onClicked: root.confirm("delete", "") }
                        }
                        PanelSeparator { Layout.fillWidth: true }
                        Text { text: "認証設定（管理者認証が必要です）"; color: Color.foreground; font.pixelSize: Style.font.subtitle }
                        RowLayout {
                            NumberField { label: "最大試行回数"; from: 1; to: 15; value: root.attempts; enabled: !root.busy; onModified: function(value) { root.attempts = value } }
                            NumberField { label: "タイムアウト（秒）"; from: 5; to: 120; value: root.timeout; enabled: !root.busy; onModified: function(value) { root.timeout = value } }
                        }
                        Repeater {
                            model: root.locations
                            ColumnLayout {
                                required property var modelData
                                Layout.fillWidth: true
                                Toggle {
                                    label: modelData.name
                                    description: !modelData.available ? "PAM サービスがありません" : modelData.native ? "既存の PAM 設定で管理されています" : "指紋認証を使用する"
                                    checked: modelData.enabled
                                    enabled: !root.busy && modelData.available && !modelData.native
                                    Layout.fillWidth: true
                                    onClicked: root.configure(modelData.name, !modelData.enabled)
                                }
                                Button { text: "試行回数とタイムアウトを適用"; focusable: true; visible: modelData.enabled && !modelData.native; enabled: !root.busy; onClicked: root.configure(modelData.name, true) }
                            }
                        }
                        PanelSeparator { Layout.fillWidth: true }
                        Text { text: "診断ログ（このパネルの操作）"; color: Color.foreground }
                        QQC.TextArea { text: root.history; readOnly: true; wrapMode: TextEdit.Wrap; color: Color.foreground; font.family: Style.font.family; Layout.fillWidth: true; Layout.preferredHeight: 120; background: Rectangle { color: "transparent" } }
                        Button { text: "ログを消去"; focusable: true; onClicked: root.history = "" }
                        Text { text: "fprintd / libfprint の更新はパッケージマネージャーで行ってください。"; color: Color.foreground; wrapMode: Text.Wrap; Layout.fillWidth: true }
                    }
                }
                ConfirmDialog {
                    id: confirmation
                    anchors.fill: parent
                    cancelText: "キャンセル"
                    confirmText: "実行"
                    onCanceled: opened = false
                    onConfirmed: { opened = false; root.run(root.pendingAction, root.pendingFinger) }
                }
            }
        }
    }
}
