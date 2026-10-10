using UnityEngine;

namespace AeroSentinel
{
    /// <summary>Maps WGS84 lat/lon to Unity world space. x = east, z = north, y = up (AGL metres).
    /// Mirrors aerosentinel_schemas.geo.to_local_m so Python and Unity agree.</summary>
    public class GeoOrigin : MonoBehaviour
    {
        public double originLat = 22.5000;
        public double originLon = 88.3000;
        const double R = 6371008.8;

        public Vector3 ToWorld(double lat, double lon, double altM = 0)
        {
            double north = (lat - originLat) * System.Math.PI / 180.0 * R;
            double east  = (lon - originLon) * System.Math.PI / 180.0 * R * System.Math.Cos(originLat * System.Math.PI / 180.0);
            return new Vector3((float)east, (float)altM, (float)north);
        }

        public (double lat, double lon, double alt) ToGeo(Vector3 w)
        {
            double lat = originLat + (w.z / R) * 180.0 / System.Math.PI;
            double lon = originLon + (w.x / (R * System.Math.Cos(originLat * System.Math.PI / 180.0))) * 180.0 / System.Math.PI;
            return (lat, lon, w.y);
        }
    }
}
