import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import io

# Page Config for Professional Look
st.set_page_config(page_title="GeoAlign Pro", page_icon="🌐", layout="wide")

# Custom CSS for Premium Styling
st.markdown("""
    <style>
    .main-header { font-size:38px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 10px; }
    .sub-header { font-size:18px !important; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .step-box { padding: 20px; background-color: #F3F4F6; border-radius: 10px; border-left: 5px solid #3B82F6; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🌐 GeoAlign Pro Studio</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">The Smartest Way to Fix Coordinate Misalignments & Map Shifts Instantly</div>', unsafe_allow_html=True)

# Layout Columns
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown('<div class="step-box"><h4>Step 1: Upload Spatial Data</h4></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drop your spatial file here (.geojson, .kml, .csv)", type=["geojson", "kml", "csv"])

    if uploaded_file is not None:
        try:
            # Load Data Safely
            if uploaded_file.name.endswith('.geojson') or uploaded_file.name.endswith('.kml'):
                gdf = gpd.read_file(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                st.info("💡 Tip: Standardized to global Lat/Lon inputs.")
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

            st.success("✅ File loaded successfully!")
            
            st.markdown('<div class="step-box"><h4>Step 2: Choose Target Projection (CRS)</h4></div>', unsafe_allow_html=True)
            crs_options = {
                "WGS 84 (Global GPS Standard) - EPSG:4326": "EPSG:4326",
                "Web Mercator (Google/Bing Maps) - EPSG:3857": "EPSG:3857",
                "UTM Zone 42N (Western Pakistan) - EPSG:32642": "EPSG:32642",
                "UTM Zone 43N (Eastern Pakistan/India) - EPSG:32643": "EPSG:32643"
            }
            selected_crs = st.selectbox("Target CRS:", list(crs_options.keys()))
            target_epsg = crs_options[selected_crs]

            st.markdown('<div class="step-box"><h4>Step 3: Align & Download</h4></div>', unsafe_allow_html=True)
            if st.button("🚀 Run Auto-Alignment", use_container_width=True):
                with st.spinner("Aligning geospatial layers..."):
                    # Transform CRS
                    transformed_gdf = gdf.to_crs(target_epsg)
                    
                    # Store transformed data for session status
                    st.session_state['transformed_gdf'] = transformed_gdf
                    st.session_state['processed'] = True
                    
                    # Convert to GeoJSON Bytes
                    output = io.BytesIO()
                    transformed_gdf.to_file(output, driver='GeoJSON', encoding='utf-8')
                    st.session_state['download_bytes'] = output.getvalue()
                    
                    st.balloons()
            
            if st.session_state.get('processed', False):
                st.download_button(
                    label="📥 Download Aligned Spatial File",
                    data=st.session_state['download_bytes'],
                    file_name=f"aligned_{uploaded_file.name}",
                    mime="application/geo+json",
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"❌ File Parsing Error: {str(e)}")
            st.info("Ensure your file has valid coordinate systems or standard 'latitude'/'longitude' columns for CSV.")

with col2:
    st.subheader("🗺️ Live Spatial Data Preview")
    if uploaded_file is not None and 'gdf' in locals():
        # Map logic (Visualize spatial input safely)
        try:
            # Always map in WGS84 for web folium display
            map_gdf = gdf.to_crs("EPSG:4326")
            center = [map_gdf.geometry.centroid.y.mean(), map_gdf.geometry.centroid.x.mean()]
            m = folium.Map(location=center, zoom_start=10, tiles="CartoDB positron")
            
            # Add spatial data to map
            folium.GeoJson(map_gdf.to_json(), name="Uploaded Data").add_to(m)
            st_folium(m, width=600, height=500)
        except:
            st.warning("⚠️ Visual map preview unavailable for this specific data structure, but alignment engine remains active.")
    else:
        st.info("Upload a file on the left to see its live geographic boundaries and mapping overlay here.")
