from flask import Flask, render_template, jsonify
from skyfield.api import load

app = Flask(__name__)

# Load planetary ephemeris data
planets = load('de421.bsp')
earth = planets['earth']

# Define the planets we want to track
planet_objects = {
    'Mercury': planets['mercury'],
    'Venus': planets['venus'],
    'Mars': planets['mars'],
    'Jupiter': planets['jupiter barycenter'],
    'Saturn': planets['saturn barycenter'],
    'Uranus': planets['uranus barycenter'],
    'Neptune': planets['neptune barycenter']
}

def get_planetary_coordinates():
    """Get current coordinates for all tracked planets"""
    ts = load.timescale()
    t = ts.now()
    
    planetary_data = []
    
    for planet_name, planet_obj in planet_objects.items():
        # Calculate apparent position from Earth
        astrometric = earth.at(t).observe(planet_obj)
        apparent = astrometric.apparent()
        
        # Get coordinates
        ra, dec, distance = apparent.radec()
        
        # Get Cartesian coordinates for 3D positioning (heliocentric)
        heliocentric = planet_obj.at(t)
        x, y, z = heliocentric.position.au
        
        # Convert to hours, minutes, seconds for RA and degrees, arcminutes, arcseconds for Dec
        ra_hours = ra.hours
        dec_degrees = dec.degrees
        distance_au = distance.au
        
        planetary_data.append({
            'name': planet_name,
            'ra_hours': ra_hours,
            'ra_formatted': f"{int(ra_hours)}h {int((ra_hours % 1) * 60)}m {((ra_hours % 1) * 60 % 1) * 60:.1f}s",
            'dec_degrees': dec_degrees,
            'dec_formatted': f"{int(dec_degrees)}° {int(abs(dec_degrees % 1) * 60)}' {(abs(dec_degrees % 1) * 60 % 1) * 60:.1f}\"",
            'distance_au': distance_au,
            'distance_formatted': f"{distance_au:.3f} AU",
            'x': x,
            'y': y,
            'z': z
        })
    
    return planetary_data, t.utc_strftime('%Y-%m-%d %H:%M:%S UTC')

@app.route('/')
def index():
    """Home route that displays planetary coordinates"""
    try:
        planetary_data, current_time = get_planetary_coordinates()
        return render_template('index.html', 
                             planets=planetary_data, 
                             current_time=current_time,
                             error=None)
    except Exception as e:
        return render_template('index.html', 
                             planets=[], 
                             current_time=None,
                             error=f"Error loading planetary data: {str(e)}")

@app.route('/3d')
def view_3d():
    """3D visualization route"""
    try:
        planetary_data, current_time = get_planetary_coordinates()
        return render_template('3d_view.html', 
                             planets=planetary_data, 
                             current_time=current_time,
                             error=None)
    except Exception as e:
        return render_template('3d_view.html', 
                             planets=[], 
                             current_time=None,
                             error=f"Error loading planetary data: {str(e)}")

@app.route('/api/planets')
def api_planets():
    """API endpoint that returns planetary coordinates as JSON"""
    try:
        planetary_data, current_time = get_planetary_coordinates()
        return jsonify({
            'success': True,
            'planets': planetary_data,
            'current_time': current_time,
            'error': None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'planets': [],
            'current_time': None,
            'error': f"Error loading planetary data: {str(e)}"
        })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
