# Opens a workbook in GridCraft and saves a screenshot of its window (PrintWindow, so it works even if the
# window is covered). The UI may not draw its final frame while the window sits idle, so a few mouse-move
# messages are posted to the window to wake it before the shot; the real cursor does not move.
#
#   .\shot_gridcraft.ps1 -Exe C:\path\gridcraft.exe -File C:\path\book.xlsx -Out C:\path\shot.png [-WaitSec 20]
param([string]$Exe, [string]$File, [string]$Out, [int]$WaitSec = 20, [int]$AfterPokeSec = 4)

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Shot {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
}
"@

$p = Start-Process -FilePath $Exe -ArgumentList "`"$File`"" -PassThru
Start-Sleep -Seconds $WaitSec
$p.Refresh()
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "no main window (pid $($p.Id))"; Stop-Process -Id $p.Id -Force; exit 1 }

# WM_MOUSEMOVE, client coordinates.
for ($i = 0; $i -lt 12; $i++) {
  $x = 300 + $i * 17; $y = 500 + $i * 9
  [void][Win32Shot]::PostMessage($h, 0x0200, [IntPtr]::Zero, [IntPtr](($y -shl 16) -bor $x))
  Start-Sleep -Milliseconds 120
}
Start-Sleep -Seconds $AfterPokeSec

$r = New-Object Win32Shot+RECT
[void][Win32Shot]::GetWindowRect($h, [ref]$r)
$w = $r.Right - $r.Left; $hh = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $hh
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[void][Win32Shot]::PrintWindow($h, $hdc, 2)
$g.ReleaseHdc($hdc)
$g.Dispose()
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Output "saved $Out ${w}x${hh} title='$($p.MainWindowTitle)'"
Stop-Process -Id $p.Id -Force
