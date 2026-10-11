using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgents.Policies;

namespace AeroSentinel
{
    public sealed class AeroSentinelTrainingEnvironment : MonoBehaviour
    {
        private readonly Vector3[] waypointPositions =
        {
            new Vector3(0f, 1.5f, 9f),
            new Vector3(10f, 1.5f, 2f),
            new Vector3(-9f, 1.5f, -7f)
        };

        private AeroSentinelAgent agent;

        private void Awake()
        {
            BuildEnvironment();
        }

        private void BuildEnvironment()
        {
            CreateCamera();
            CreateLighting();
            CreatePrimitive("Ground", PrimitiveType.Cube, new Vector3(0f, -0.5f, 0f), new Vector3(28f, 1f, 28f), new Color(0.16f, 0.22f, 0.2f));

            GameObject dockObject = CreatePrimitive("Dock", PrimitiveType.Cylinder, new Vector3(0f, 0.1f, -10f), new Vector3(3f, 0.2f, 3f), new Color(0.15f, 0.6f, 0.8f));
            DockingStation dock = dockObject.AddComponent<DockingStation>();

            for (int index = 0; index < waypointPositions.Length; index++)
            {
                GameObject waypointObject = CreatePrimitive("Waypoint_" + index, PrimitiveType.Cylinder, waypointPositions[index], new Vector3(1.2f, 0.15f, 1.2f), new Color(0.9f, 0.75f, 0.2f));
                waypointObject.AddComponent<PatrolWaypoint>().Index = index;
            }

            GameObject anomalyObject = CreatePrimitive("SyntheticAnomaly", PrimitiveType.Sphere, new Vector3(8f, 0.8f, 6f), new Vector3(2f, 1.6f, 2f), new Color(0.9f, 0.2f, 0.12f));
            DisasterSource source = anomalyObject.AddComponent<DisasterSource>();
            source.Severity = 0.85f;

            GameObject droneObject = CreatePrimitive("Drone", PrimitiveType.Sphere, dock.transform.position + Vector3.up * 1.5f, Vector3.one, new Color(0.85f, 0.9f, 0.95f));
            SimulatedDroneController controller = droneObject.AddComponent<SimulatedDroneController>();
            controller.Dock = dock;
            controller.Waypoints = FindWaypoints();
            droneObject.AddComponent<SyntheticSensor>();
            agent = droneObject.AddComponent<AeroSentinelAgent>();
            BehaviorParameters behavior = droneObject.AddComponent<BehaviorParameters>();
            behavior.BrainParameters.VectorObservationSize = 18;
            behavior.BrainParameters.ActionSpec = ActionSpec.MakeDiscrete(5);
            behavior.BehaviorType = BehaviorType.Default;
            behavior.BehaviorName = "AeroSentinelMissionPolicy";
            DecisionRequester requester = droneObject.AddComponent<DecisionRequester>();
            requester.DecisionPeriod = 5;
            agent.Controller = controller;
            agent.Anomaly = source;
            agent.Waypoints = controller.Waypoints;
        }

        private static void CreateCamera()
        {
            GameObject cameraObject = new GameObject("TrainingCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0f, 24f, -25f);
            cameraObject.transform.rotation = Quaternion.Euler(38f, 0f, 0f);
            camera.fieldOfView = 55f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.06f, 0.09f, 0.12f);
        }

        private static void CreateLighting()
        {
            GameObject lightObject = new GameObject("TrainingSun");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.2f;
            lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        }

        private PatrolWaypoint[] FindWaypoints()
        {
            return FindObjectsByType<PatrolWaypoint>();
        }

        private static GameObject CreatePrimitive(string objectName, PrimitiveType primitiveType, Vector3 position, Vector3 scale, Color color)
        {
            GameObject item = GameObject.CreatePrimitive(primitiveType);
            item.name = objectName;
            item.transform.position = position;
            item.transform.localScale = scale;
            Renderer renderer = item.GetComponent<Renderer>();
            renderer.material.color = color;
            return item;
        }

        private void OnGUI()
        {
            if (agent == null || agent.Controller == null)
            {
                return;
            }

            GUI.Label(new Rect(16f, 16f, 500f, 24f), "AeroSentinel Training | Battery: " + agent.Controller.Battery.ToString("0.00") + " | State: " + agent.Controller.State);
            GUI.Label(new Rect(16f, 40f, 700f, 24f), "Actions: 0 Continue | 1 Investigate | 2 Next waypoint | 3 Return | 4 Recharge");
        }
    }
}
