using System;
using System.Collections;
using UnityEngine;

namespace AeroSentinel
{
    /// <summary>Kinematic drone + battery model. Swap for PX4/Gazebo-driven motion later (ADR-0002);
    /// the bridge only talks to this class, so the Python side does not change.</summary>
    public class DroneController : MonoBehaviour
    {
        public GeoOrigin origin;
        public Transform dock;                 // docking station transform (B3)
        public float batteryPct = 100f;
        public float drainPctPerKm = 4f;       // keep equal to MockDrone for sim parity
        public string Mode { get; private set; } = "docked";

        public IEnumerator FlyTo(Vector3 target, float speed, Action<string> onDone)
        {
            float km = Vector3.Distance(transform.position, target) / 1000f;
            float cost = km * drainPctPerKm;
            if (cost > batteryPct) { Mode = "error"; onDone("battery depleted in flight"); yield break; }
            Mode = "flying";
            while ((transform.position - target).sqrMagnitude > 0.04f)
            {
                transform.position = Vector3.MoveTowards(transform.position, target, Mathf.Max(speed, 0.1f) * Time.deltaTime);
                yield return null;
            }
            batteryPct -= cost;
            onDone(null);
        }

        public IEnumerator Dock(Action<string> onDone)
        {
            string err = null;
            yield return FlyTo(dock.position, 10f, e => err = e);
            if (err == null) Mode = "docked";
            onDone(err);
        }

        public void Recharge() { batteryPct = 100f; }   // TODO(B3/C2): timed charging at the dock
    }
}
