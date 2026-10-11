using UnityEngine;

namespace AeroSentinel
{
    public sealed class SyntheticSensor : MonoBehaviour
    {
        public float Temperature { get; private set; }
        public float Smoke { get; private set; }
        public float Humidity { get; private set; }

        public void Read(DisasterSource source)
        {
            float anomaly = source == null ? 0f : source.GetAnomalyStrength(transform.position);
            Temperature = Mathf.Clamp01(0.25f + anomaly * 0.75f);
            Smoke = Mathf.Clamp01(anomaly * 1.1f);
            Humidity = Mathf.Clamp01(0.6f - anomaly * 0.35f);
        }
    }
}
