using UnityEngine;

namespace AeroSentinel
{
    public interface IDroneController
    {
        Vector3 Position { get; }
        Vector3 Velocity { get; }
        float Battery { get; }
        DroneMissionState State { get; }
        bool IsAtDock { get; }
        void TakeOff();
        void MoveTo(Vector3 destination);
        void ReturnToDock();
        void Recharge();
        void ResetDrone();
    }

    public enum DroneMissionState
    {
        Docked,
        Patrolling,
        Investigating,
        Returning,
        Charging
    }
}
