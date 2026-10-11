using UnityEngine;

namespace AeroSentinel
{
    public sealed class SimulatedDroneController : MonoBehaviour, IDroneController
    {
        [SerializeField] private float speed = 5f;
        [SerializeField] private float batteryCapacity = 100f;
        [SerializeField] private float batteryConsumptionPerSecond = 2f;
        [SerializeField] private float minimumReturnBattery = 15f;

        public DockingStation Dock { get; set; }
        public PatrolWaypoint[] Waypoints { get; set; }
        public Vector3 Position => transform.position;
        public Vector3 Velocity { get; private set; }
        public float Battery { get; private set; }
        public DroneMissionState State { get; private set; }
        public bool IsAtDock => Dock != null && Vector3.Distance(transform.position, Dock.transform.position + Vector3.up * 1.5f) < 0.75f;
        public float MinimumReturnBattery => minimumReturnBattery;

        private Vector3 destination;

        private void Awake()
        {
            ResetDrone();
        }

        private void Update()
        {
            if (State == DroneMissionState.Docked || State == DroneMissionState.Charging)
            {
                Velocity = Vector3.zero;
                return;
            }

            Vector3 previousPosition = transform.position;
            transform.position = Vector3.MoveTowards(transform.position, destination, speed * Time.deltaTime);
            Velocity = (transform.position - previousPosition) / Mathf.Max(Time.deltaTime, 0.0001f);
            Battery = Mathf.Max(0f, Battery - batteryConsumptionPerSecond * Time.deltaTime);

            if (Vector3.Distance(transform.position, destination) < 0.1f && State == DroneMissionState.Returning && IsAtDock)
            {
                State = DroneMissionState.Docked;
            }

            if (Battery <= minimumReturnBattery && State != DroneMissionState.Returning)
            {
                ReturnToDock();
            }
        }

        public void TakeOff()
        {
            if (State == DroneMissionState.Docked)
            {
                State = DroneMissionState.Patrolling;
                destination = transform.position + Vector3.up;
            }
        }

        public void MoveTo(Vector3 target)
        {
            TakeOff();
            destination = target;
            State = DroneMissionState.Patrolling;
        }

        public void ReturnToDock()
        {
            if (Dock == null)
            {
                return;
            }

            TakeOff();
            destination = Dock.transform.position + Vector3.up * 1.5f;
            State = DroneMissionState.Returning;
        }

        public void Recharge()
        {
            if (IsAtDock)
            {
                State = DroneMissionState.Charging;
                Battery = batteryCapacity;
                State = DroneMissionState.Docked;
            }
        }

        public void ResetDrone()
        {
            if (Dock != null)
            {
                transform.position = Dock.transform.position + Vector3.up * 1.5f;
            }

            Battery = batteryCapacity;
            Velocity = Vector3.zero;
            State = DroneMissionState.Docked;
            destination = transform.position;
        }
    }
}
