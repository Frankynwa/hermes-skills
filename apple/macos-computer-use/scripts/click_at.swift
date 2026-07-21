import CoreGraphics

let args = CommandLine.arguments
guard args.count == 3,
      let x = Float(args[1]),
      let y = Float(args[2]) else {
    print("Usage: click_at.swift <x> <y>")
    exit(1)
}

let point = CGPoint(x: CGFloat(x), y: CGFloat(y))

// Post click events at position. WARNING: CGEvent with cghidEventTap
// may briefly move the user's visible cursor. This is NOT background-safe
// like cua-driver. Warn the user before using.
if let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown,
    mouseCursorPosition: point, mouseButton: .left) {
    down.post(tap: .cghidEventTap)
    usleep(80000)
}
if let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp,
    mouseCursorPosition: point, mouseButton: .left) {
    up.post(tap: .cghidEventTap)
}

print("Clicked at (\(x), \(y))")
