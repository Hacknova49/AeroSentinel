using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace AeroSentinel
{
    [System.Serializable]
    public class FloodScenario
    {
        public string hazard = "flood";
        public double centerLat = 22.5045, centerLon = 88.3045;
        public float startS = 0f;                 // scenario time at which the flood begins
        public float growthMPerHour = 200f;
        public float maxDepthM = 2.5f;
    }

    /// <summary>B4: time-evolving hazards with ground truth. Load scenario JSON from Assets/AeroSentinel/Scenarios.
    /// TODO(member 5): fire spread, landslide, structural damage; reuse the same ground-truth log format.</summary>
    public class ScenarioEngine : MonoBehaviour
    {
        public GeoOrigin origin;
        public TextAsset scenarioJson;
        public float timeScale = 60f;             // 1 real second = 60 scenario seconds
        public float ScenarioTimeS { get; private set; }
        FloodScenario flood = new FloodScenario();

        void Awake() { if (scenarioJson != null) flood = JsonUtility.FromJson<FloodScenario>(scenarioJson.text); }
        void Update() { ScenarioTimeS += Time.deltaTime * timeScale; }

        public float FloodRadiusM() => Mathf.Max(0f, (ScenarioTimeS - flood.startS) / 3600f * flood.growthMPerHour);

        /// <summary>Ground-truth water depth (m) at a world position.</summary>
        public float WaterDepthAt(Vector3 world)
        {
            Vector3 c = origin.ToWorld(flood.centerLat, flood.centerLon);
            float d = Vector2.Distance(new Vector2(world.x, world.z), new Vector2(c.x, c.z));
            float r = FloodRadiusM();
            return d >= r ? 0f : flood.maxDepthM * (1f - d / r);
        }

        public void LogTruth(string path, string zoneId, Vector3 world)
        {
            File.AppendAllText(path, JsonUtility.ToJson(new TruthRow {
                t = ScenarioTimeS, zone_id = zoneId, hazard = flood.hazard, depth_m = WaterDepthAt(world) }) + "\n");
        }
        [System.Serializable] class TruthRow { public float t; public string zone_id, hazard; public float depth_m; }
    }
}
