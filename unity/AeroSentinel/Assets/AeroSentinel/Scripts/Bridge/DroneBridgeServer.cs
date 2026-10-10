using System;
using System.Collections;
using System.Collections.Concurrent;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Newtonsoft.Json.Linq;     // Package Manager: com.unity.nuget.newtonsoft-json
using UnityEngine;

namespace AeroSentinel
{
    /// <summary>TCP JSON-lines server matching python/src/aerosentinel/autonomy/unity_drone.py.
    /// Socket I/O runs on a background thread; every command executes on the Unity main thread.
    /// NOTE: written without a Unity compile pass - expect to fix small API/typo issues on first run.</summary>
    public class DroneBridgeServer : MonoBehaviour
    {
        public int port = 5555;
        public GeoOrigin origin;
        public DroneController drone;
        public VirtualSensorSuite sensors;

        class Req { public JObject Json; public StreamWriter Out; }
        readonly ConcurrentQueue<Req> queue = new ConcurrentQueue<Req>();
        TcpListener listener; Thread thread; volatile bool running;

        void Start()
        {
            running = true;
            listener = new TcpListener(IPAddress.Loopback, port); listener.Start();
            thread = new Thread(Accept) { IsBackground = true }; thread.Start();
            Debug.Log($"[AeroSentinel] bridge listening on 127.0.0.1:{port}");
        }

        void OnDestroy() { running = false; listener?.Stop(); }

        void Accept()
        {
            while (running)
            {
                try
                {
                    var client = listener.AcceptTcpClient();
                    new Thread(() => Serve(client)) { IsBackground = true }.Start();
                }
                catch (SocketException) { }
            }
        }

        void Serve(TcpClient client)
        {
            using (client)
            using (var r = new StreamReader(client.GetStream()))
            using (var w = new StreamWriter(client.GetStream()) { NewLine = "\n", AutoFlush = true })
            {
                string line;
                while (running && (line = r.ReadLine()) != null)
                    queue.Enqueue(new Req { Json = JObject.Parse(line), Out = w });
            }
        }

        void Update()
        {
            while (queue.TryDequeue(out var req)) StartCoroutine(Handle(req));
        }

        static void Reply(Req q, object result, string error = null)
        {
            var o = new JObject { ["id"] = q.Json["id"], ["ok"] = error == null };
            if (error == null) o["result"] = result == null ? new JObject() : JToken.FromObject(result);
            else o["error"] = error;
            lock (q.Out) q.Out.WriteLine(o.ToString(Newtonsoft.Json.Formatting.None));
        }

        string Now() => DateTime.UtcNow.ToString("o");

        object State()
        {
            var g = origin.ToGeo(drone.transform.position);
            return new { position = new { lat = g.lat, lon = g.lon, alt_m = g.alt }, battery_pct = drone.batteryPct,
                         mode = drone.Mode, timestamp = Now() };
        }

        IEnumerator Handle(Req q)
        {
            string cmd = (string)q.Json["cmd"]; var a = (JObject)q.Json["args"];
            string err = null;
            switch (cmd)
            {
                case "fly_to":
                    var target = origin.ToWorld((double)a["lat"], (double)a["lon"], (double)a["alt_m"]);
                    yield return drone.FlyTo(target, (float)a["speed_mps"], e => err = e);
                    Reply(q, err == null ? new { reached = true } : null, err); break;
                case "dock":
                    yield return drone.Dock(e => err = e);
                    if (err == null) drone.Recharge();   // TODO: real charge time via dock model (C2)
                    Reply(q, new { docked = err == null }, err); break;
                case "get_state": Reply(q, State()); break;
                case "battery_level": Reply(q, new { battery_pct = drone.batteryPct }); break;
                case "capture":
                    var rows = new JArray(); var pos = drone.transform.position; var g = origin.ToGeo(pos);
                    foreach (var s in a["sensors"])
                    {
                        string sensor = (string)s, id = "obs-" + Guid.NewGuid().ToString("N").Substring(0, 12);
                        var row = new JObject {
                            ["id"] = id, ["region_id"] = a["region_id"], ["zone_id"] = a["zone_id"], ["patrol_id"] = a["patrol_id"],
                            ["sensor"] = sensor, ["timestamp"] = Now(),
                            ["position"] = new JObject { ["lat"] = g.lat, ["lon"] = g.lon, ["alt_m"] = g.alt },
                            ["image_uri"] = (sensor == "rgb") ? sensors.CaptureRgb(id) : null,
                            ["readings"] = JObject.FromObject(sensors.Scalar(sensor, pos)) };
                        rows.Add(row);
                    }
                    Reply(q, rows); break;
                default: Reply(q, null, "unknown command: " + cmd); break;
            }
        }
    }
}
