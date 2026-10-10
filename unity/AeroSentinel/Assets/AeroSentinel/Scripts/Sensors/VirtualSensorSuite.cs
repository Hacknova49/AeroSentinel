using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace AeroSentinel
{
    /// <summary>B5: virtual sensors with noise models. Scalar sensors read ScenarioEngine ground truth + noise.
    /// RGB renders the drone camera to PNG and returns its path (image_uri). Thermal/weather: TODO(member 5).</summary>
    public class VirtualSensorSuite : MonoBehaviour
    {
        public ScenarioEngine scenario;
        public Camera rgbCamera;
        public int imageWidth = 640, imageHeight = 640;
        public float waterLevelNoiseSd = 0.02f;
        public string captureDir = "captures";

        static float Gauss(float sd)
        {
            float u1 = 1f - Random.value, u2 = Random.value;
            return sd * Mathf.Sqrt(-2f * Mathf.Log(u1)) * Mathf.Cos(2f * Mathf.PI * u2);
        }

        public Dictionary<string, float> Scalar(string sensor, Vector3 pos)
        {
            switch (sensor)
            {
                case "water_level":   return new Dictionary<string, float> { { "water_level_m", Mathf.Max(0f, scenario.WaterDepthAt(pos) + Gauss(waterLevelNoiseSd)) } };
                case "rainfall":      return new Dictionary<string, float> { { "rain_mm_h", Mathf.Max(0f, 5f + Gauss(1f)) } };   // TODO: weather system
                case "soil_moisture": return new Dictionary<string, float> { { "soil_moisture", Mathf.Clamp01(0.5f + Gauss(0.05f)) } };
                default:              return new Dictionary<string, float>();
            }
        }

        public string CaptureRgb(string obsId)
        {
            Directory.CreateDirectory(captureDir);
            var rt = new RenderTexture(imageWidth, imageHeight, 24);
            var prev = rgbCamera.targetTexture;
            rgbCamera.targetTexture = rt; rgbCamera.Render(); rgbCamera.targetTexture = prev;
            var tex = new Texture2D(imageWidth, imageHeight, TextureFormat.RGB24, false);
            RenderTexture.active = rt; tex.ReadPixels(new Rect(0, 0, imageWidth, imageHeight), 0, 0); tex.Apply();
            RenderTexture.active = null;
            string path = Path.GetFullPath(Path.Combine(captureDir, obsId + ".png"));
            File.WriteAllBytes(path, tex.EncodeToPNG());
            Destroy(rt); Destroy(tex);
            return path;
        }
    }
}
