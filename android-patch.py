# بيتشغل أوتوماتيك جوه GitHub Actions بعد ما Capacitor يعمل مشروع الأندرويد.
import os, re

run = os.environ.get("RUN", "1")
pkg = "com.waqfa.app"

# 1) الصلاحيات
man = "android/app/src/main/AndroidManifest.xml"
s = open(man, encoding="utf-8").read()
if "android.permission.CAMERA" not in s:
    add = "".join('    <uses-permission android:name="%s" />\n' % x for x in [
        "android.permission.CAMERA",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.WAKE_LOCK"])
    add += '    <uses-feature android:name="android.hardware.camera" android:required="false" />\n'
    assert "</manifest>" in s
    s = s.replace("</manifest>", add + "</manifest>")
    open(man, "w", encoding="utf-8").write(s)

# 2) الشاشة تفضل منورة (والصفحة بتقفلها لما مفيش تصوير)
java = """package com.waqfa.app;

import android.os.Bundle;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    getBridge().getWebView().addJavascriptInterface(new KeepAwake(), "WaqfaNative");
  }

  private class KeepAwake {
    @JavascriptInterface
    public void keepOn(final boolean on) {
      runOnUiThread(new Runnable() {
        @Override
        public void run() {
          if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
          else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        }
      });
    }
  }
}
"""
d = "android/app/src/main/java/" + pkg.replace(".", "/")
os.makedirs(d, exist_ok=True)
open(d + "/MainActivity.java", "w", encoding="utf-8").write(java)

# 3) رقم الإصدار يزيد مع كل بناء
g = "android/app/build.gradle"
t = open(g, encoding="utf-8").read()
t = re.sub(r"versionCode\s+\d+", "versionCode " + run, t)
t = re.sub(r'versionName\s+"[^"]*"', 'versionName "1.0.' + run + '"', t)
open(g, "w", encoding="utf-8").write(t)
print("patched OK, build", run)
