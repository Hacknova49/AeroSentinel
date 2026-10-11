using UnityEngine;

namespace AeroSentinel
{
    public sealed class DisasterSource : MonoBehaviour
    {
        [Range(0f, 1f)] public float Severity = 0.85f;
        public bool IsActive = true;
        public float ActivationTime;

        public float GetAnomalyStrength(Vector3 observerPosition)
        {
            if (!IsActive)
            {
                return 0f;
            }

            float distance = Vector3.Distance(observerPosition, transform.position);
            return Mathf.Clamp01(Severity * Mathf.Exp(-distance * 0.12f));
        }
    }
}
