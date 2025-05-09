from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QGroupBox, QFormLayout, QCheckBox,
    QLineEdit, QTabWidget, QSplitter, QMenu, QToolBar, QFileDialog,
    QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize  # Add QSize here
from PyQt6.QtGui import QIcon, QColor, QAction 
from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6.QtWebEngineCore import QWebEngineSettings
import os
import json
import tempfile

class MapWidget(QWidget):
    """
    Widget for displaying and interacting with maps
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.initialize_map()
    
    def setup_ui(self):
        """Set up the map UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # Zoom controls
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(self.zoom_out_action)
        
        toolbar.addSeparator()
        
        # Map type
        toolbar.addWidget(QLabel("Map Type:"))
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(["OpenStreetMap", "CartoDB Positron", "CartoDB Dark Matter"])
        self.map_type_combo.currentTextChanged.connect(self.change_map_type)
        toolbar.addWidget(self.map_type_combo)
        
        toolbar.addSeparator()
        
        # Location search
        toolbar.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter location...")
        self.search_input.returnPressed.connect(self.search_location)
        toolbar.addWidget(self.search_input)
        
        self.search_button = QPushButton("Go")
        self.search_button.clicked.connect(self.search_location)
        toolbar.addWidget(self.search_button)
        
        toolbar.addSeparator()
        
        # View options
        self.toggle_markers_action = QAction("Toggle Markers", self)
        self.toggle_markers_action.setCheckable(True)
        self.toggle_markers_action.setChecked(True)
        self.toggle_markers_action.triggered.connect(self.toggle_markers)
        toolbar.addAction(self.toggle_markers_action)
        
        self.toggle_heatmap_action = QAction("Heatmap", self)
        self.toggle_heatmap_action.setCheckable(True)
        self.toggle_heatmap_action.triggered.connect(self.toggle_heatmap)
        toolbar.addAction(self.toggle_heatmap_action)
        
        layout.addWidget(toolbar)
        
        # Create splitter for map and sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Map view
        self.map_view = QWebEngineView()
        self.map_view.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.map_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.map_view.setMinimumSize(400, 300)
        
        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Layers tab widget
        tabs = QTabWidget()
        
        # Layers tab
        layers_tab = QWidget()
        layers_layout = QVBoxLayout(layers_tab)
        
        self.base_layer_group = QGroupBox("Base Layer")
        base_layer_layout = QVBoxLayout(self.base_layer_group)
        
        self.osm_radio = QCheckBox("OpenStreetMap")
        self.osm_radio.setChecked(True)
        self.osm_radio.stateChanged.connect(lambda: self.map_type_combo.setCurrentText("OpenStreetMap"))
        
        self.carto_light_radio = QCheckBox("CartoDB Light")
        self.carto_light_radio.stateChanged.connect(lambda: self.map_type_combo.setCurrentText("CartoDB Positron"))
        
        self.carto_dark_radio = QCheckBox("CartoDB Dark")
        self.carto_dark_radio.stateChanged.connect(lambda: self.map_type_combo.setCurrentText("CartoDB Dark Matter"))
        
        base_layer_layout.addWidget(self.osm_radio)
        base_layer_layout.addWidget(self.carto_light_radio)
        base_layer_layout.addWidget(self.carto_dark_radio)
        
        layers_layout.addWidget(self.base_layer_group)
        
        # Overlay layers
        self.overlay_group = QGroupBox("Overlay Layers")
        overlay_layout = QVBoxLayout(self.overlay_group)
        
        self.markers_check = QCheckBox("Markers")
        self.markers_check.setChecked(True)
        self.markers_check.stateChanged.connect(lambda state: self.toggle_markers_action.setChecked(state))
        
        self.heatmap_check = QCheckBox("Heatmap")
        self.heatmap_check.stateChanged.connect(lambda state: self.toggle_heatmap_action.setChecked(state))
        
        self.grid_check = QCheckBox("Grid")
        self.grid_check.stateChanged.connect(self.toggle_grid)
        
        overlay_layout.addWidget(self.markers_check)
        overlay_layout.addWidget(self.heatmap_check)
        overlay_layout.addWidget(self.grid_check)
        
        layers_layout.addWidget(self.overlay_group)
        
        # Add spacer
        layers_layout.addStretch(1)
        
        tabs.addTab(layers_tab, "Layers")
        
        # Data tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        
        self.load_data_button = QPushButton("Load Data")
        self.load_data_button.clicked.connect(self.load_data)
        
        self.clear_data_button = QPushButton("Clear Data")
        self.clear_data_button.clicked.connect(self.clear_data)
        
        data_layout.addWidget(self.load_data_button)
        data_layout.addWidget(self.clear_data_button)
        
        # Data info section
        self.data_info_group = QGroupBox("Data Information")
        data_info_layout = QFormLayout(self.data_info_group)
        
        self.data_source_label = QLabel("No data loaded")
        data_info_layout.addRow("Source:", self.data_source_label)
        
        self.data_points_label = QLabel("0")
        data_info_layout.addRow("Points:", self.data_points_label)
        
        data_layout.addWidget(self.data_info_group)
        
        # Add spacer
        data_layout.addStretch(1)
        
        tabs.addTab(data_tab, "Data")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Map settings
        map_settings_group = QGroupBox("Map Settings")
        map_settings_layout = QFormLayout(map_settings_group)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(1, 18)
        self.zoom_slider.setValue(13)
        self.zoom_slider.valueChanged.connect(self.zoom_to_level)
        map_settings_layout.addRow("Zoom Level:", self.zoom_slider)
        
        self.auto_center_check = QCheckBox("Auto-center on data")
        self.auto_center_check.setChecked(True)
        map_settings_layout.addRow("", self.auto_center_check)
        
        settings_layout.addWidget(map_settings_group)
        
        # Appearance settings
        appearance_group = QGroupBox("Appearance Settings")
        appearance_layout = QFormLayout(appearance_group)
        
        self.marker_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.marker_size_slider.setRange(5, 30)
        self.marker_size_slider.setValue(10)
        self.marker_size_slider.valueChanged.connect(self.update_marker_size)
        appearance_layout.addRow("Marker Size:", self.marker_size_slider)
        
        self.heatmap_radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.heatmap_radius_slider.setRange(5, 50)
        self.heatmap_radius_slider.setValue(25)
        self.heatmap_radius_slider.valueChanged.connect(self.update_heatmap_radius)
        appearance_layout.addRow("Heatmap Radius:", self.heatmap_radius_slider)
        
        settings_layout.addWidget(appearance_group)
        
        # Add spacer
        settings_layout.addStretch(1)
        
        tabs.addTab(settings_tab, "Settings")
        
        sidebar_layout.addWidget(tabs)
        
        # Add map view and sidebar to splitter
        splitter.addWidget(self.map_view)
        splitter.addWidget(sidebar)
        
        # Set relative sizes (70% map, 30% sidebar)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
    
    def initialize_map(self):
        """Initialize the map with Leaflet.js"""
        # Create a basic HTML with Leaflet map
        map_html = self._get_map_html()
        
        # Create a temporary file to host the map
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        self.temp_file.write(map_html.encode('utf-8'))
        self.temp_file.close()
        
        # Load the map file
        self.map_view.load(QUrl.fromLocalFile(self.temp_file.name))
    
    def _get_map_html(self):
        """Generate HTML for the map"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Secure GUI Platform Map</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
            <style>
                html, body, #map {
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([37.7749, -122.4194], 13);
                
                // Base layers
                var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);
                
                var cartoLight = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attribution">CARTO</a>'
                });
                
                var cartoDark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attribution">CARTO</a>'
                });
                
                var baseLayers = {
                    "OpenStreetMap": osm,
                    "CartoDB Positron": cartoLight,
                    "CartoDB Dark Matter": cartoDark
                };
                
                // Overlay layers
                var markers = L.layerGroup().addTo(map);
                var heatmapLayer = null;
                var gridLayer = null;
                
                // Data layers
                var dataPoints = [];
                
                // Function to change base layer
                function changeBaseLayer(name) {
                    if (name === "OpenStreetMap") {
                        map.removeLayer(cartoLight);
                        map.removeLayer(cartoDark);
                        map.addLayer(osm);
                    } else if (name === "CartoDB Positron") {
                        map.removeLayer(osm);
                        map.removeLayer(cartoDark);
                        map.addLayer(cartoLight);
                    } else if (name === "CartoDB Dark Matter") {
                        map.removeLayer(osm);
                        map.removeLayer(cartoLight);
                        map.addLayer(cartoDark);
                    }
                }
                
                // Function to toggle markers
                function toggleMarkers(show) {
                    if (show) {
                        map.addLayer(markers);
                    } else {
                        map.removeLayer(markers);
                    }
                }
                
                // Function to toggle heatmap
                function toggleHeatmap(show) {
                    if (show) {
                        if (heatmapLayer) {
                            map.addLayer(heatmapLayer);
                        } else if (dataPoints.length > 0) {
                            heatmapLayer = L.heatLayer(dataPoints, { radius: 25 }).addTo(map);
                        }
                    } else if (heatmapLayer) {
                        map.removeLayer(heatmapLayer);
                    }
                }
                
                // Function to toggle grid
                function toggleGrid(show) {
                    if (show) {
                        if (!gridLayer) {
                            // Create a grid overlay
                            gridLayer = L.layerGroup();
                            var bounds = map.getBounds();
                            var north = bounds.getNorth();
                            var south = bounds.getSouth();
                            var east = bounds.getEast();
                            var west = bounds.getWest();
                            
                            // Create vertical lines
                            for (var lon = Math.floor(west); lon <= Math.ceil(east); lon += 0.5) {
                                L.polyline([[south, lon], [north, lon]], {color: 'rgba(0,0,0,0.3)', weight: 1}).addTo(gridLayer);
                            }
                            
                            // Create horizontal lines
                            for (var lat = Math.floor(south); lat <= Math.ceil(north); lat += 0.5) {
                                L.polyline([[lat, west], [lat, east]], {color: 'rgba(0,0,0,0.3)', weight: 1}).addTo(gridLayer);
                            }
                        }
                        map.addLayer(gridLayer);
                    } else if (gridLayer) {
                        map.removeLayer(gridLayer);
                    }
                }
                
                // Function to add data points
                function loadData(data) {
                    markers.clearLayers();
                    dataPoints = [];
                    
                    // Remove existing heatmap
                    if (heatmapLayer) {
                        map.removeLayer(heatmapLayer);
                        heatmapLayer = null;
                    }
                    
                    // Add markers and collect points for heatmap
                    for (var i = 0; i < data.length; i++) {
                        var point = data[i];
                        var marker = L.marker([point.lat, point.lng]);
                        
                        if (point.popup) {
                            marker.bindPopup(point.popup);
                        }
                        
                        markers.addLayer(marker);
                        dataPoints.push([point.lat, point.lng, point.intensity || 1]);
                    }
                    
                    // Create new heatmap if enabled
                    if (document.getElementById('heatmapEnabled').checked) {
                        heatmapLayer = L.heatLayer(dataPoints, { radius: 25 }).addTo(map);
                    }
                    
                    // Auto center if enabled
                    if (document.getElementById('autoCenterEnabled').checked && data.length > 0) {
                        var bounds = markers.getBounds();
                        map.fitBounds(bounds, { padding: [50, 50] });
                    }
                }
                
                // Function to clear data
                function clearData() {
                    markers.clearLayers();
                    dataPoints = [];
                    
                    if (heatmapLayer) {
                        map.removeLayer(heatmapLayer);
                        heatmapLayer = null;
                    }
                }
                
                // Function to search location
                function searchLocation(query) {
                    // This would ideally use a geocoding service
                    // For demo, we'll use a simple lookup of some cities
                    var cities = {
                        'san francisco': [37.7749, -122.4194],
                        'new york': [40.7128, -74.0060],
                        'los angeles': [34.0522, -118.2437],
                        'chicago': [41.8781, -87.6298],
                        'london': [51.5074, -0.1278],
                        'paris': [48.8566, 2.3522],
                        'tokyo': [35.6762, 139.6503],
                        'sydney': [-33.8688, 151.2093],
                        'rio de janeiro': [-22.9068, -43.1729],
                        'cape town': [-33.9249, 18.4241]
                    };
                    
                    var q = query.toLowerCase();
                    if (cities[q]) {
                        map.setView(cities[q], 12);
                        return true;
                    }
                    return false;
                }
                
                // Function to update marker size
                function updateMarkerSize(size) {
                    // This would need custom markers to implement
                    console.log('Marker size updated to ' + size);
                }
                
                // Function to update heatmap radius
                function updateHeatmapRadius(radius) {
                    if (heatmapLayer) {
                        map.removeLayer(heatmapLayer);
                        heatmapLayer = L.heatLayer(dataPoints, { radius: radius }).addTo(map);
                    }
                }
                
                // Add hidden checkboxes for PyQt to interact with
                document.body.innerHTML += '<input type="checkbox" id="heatmapEnabled" style="display:none;">';
                document.body.innerHTML += '<input type="checkbox" id="markersEnabled" style="display:none;" checked>';
                document.body.innerHTML += '<input type="checkbox" id="gridEnabled" style="display:none;">';
                document.body.innerHTML += '<input type="checkbox" id="autoCenterEnabled" style="display:none;" checked>';
            </script>
        </body>
        </html>
        """
    
    def zoom_in(self):
        """Zoom in on the map"""
        current_zoom = self.zoom_slider.value()
        self.zoom_slider.setValue(min(current_zoom + 1, 18))
    
    def zoom_out(self):
        """Zoom out on the map"""
        current_zoom = self.zoom_slider.value()
        self.zoom_slider.setValue(max(current_zoom - 1, 1))
    
    def zoom_to_level(self, level):
        """Zoom to a specific level"""
        self.map_view.page().runJavaScript(f"map.setZoom({level});")
    
    def change_map_type(self, map_type):
        """Change the base map type"""
        # Update radio buttons
        self.osm_radio.setChecked(map_type == "OpenStreetMap")
        self.carto_light_radio.setChecked(map_type == "CartoDB Positron")
        self.carto_dark_radio.setChecked(map_type == "CartoDB Dark Matter")
        
        # Update map
        self.map_view.page().runJavaScript(f"changeBaseLayer('{map_type}');")
    
    def toggle_markers(self, show):
        """Toggle marker visibility"""
        self.markers_check.setChecked(show)
        self.map_view.page().runJavaScript(f"toggleMarkers({str(show).lower()});")
        self.map_view.page().runJavaScript(f"document.getElementById('markersEnabled').checked = {str(show).lower()};")
    
    def toggle_heatmap(self, show):
        """Toggle heatmap visibility"""
        self.heatmap_check.setChecked(show)
        self.map_view.page().runJavaScript(f"toggleHeatmap({str(show).lower()});")
        self.map_view.page().runJavaScript(f"document.getElementById('heatmapEnabled').checked = {str(show).lower()};")
    
    def toggle_grid(self, show):
        """Toggle grid visibility"""
        self.map_view.page().runJavaScript(f"toggleGrid({str(show).lower()});")
        self.map_view.page().runJavaScript(f"document.getElementById('gridEnabled').checked = {str(show).lower()};")
    
    def search_location(self):
        """Search for a location"""
        query = self.search_input.text()
        if not query:
            return
        
        self.map_view.page().runJavaScript(
            f"searchLocation('{query}');",
            lambda success: self.handle_search_result(success, query)
        )
    
    def handle_search_result(self, success, query):
        """Handle search result"""
        if not success:
            QMessageBox.warning(self, "Location Search", f"Location '{query}' not found.")
    
    def update_marker_size(self, size):
        """Update marker size"""
        self.map_view.page().runJavaScript(f"updateMarkerSize({size});")
    
    def update_heatmap_radius(self, radius):
        """Update heatmap radius"""
        self.map_view.page().runJavaScript(f"updateHeatmapRadius({radius});")
    
    def load_data(self):
        """Load data from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Data",
            "",
            "GeoJSON Files (*.geojson);;JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            data_points = []
            
            if file_path.endswith('.geojson') or file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Process GeoJSON format
                if 'type' in data and data['type'] == 'FeatureCollection':
                    for feature in data['features']:
                        if feature['geometry']['type'] == 'Point':
                            lon, lat = feature['geometry']['coordinates']
                            properties = feature['properties'] if 'properties' in feature else {}
                            
                            point = {
                                'lat': lat,
                                'lng': lon,
                                'intensity': properties.get('intensity', 1)
                            }
                            
                            # Create popup content from properties
                            if properties:
                                popup = "<div>"
                                for key, value in properties.items():
                                    popup += f"<strong>{key}:</strong> {value}<br>"
                                popup += "</div>"
                                point['popup'] = popup
                            
                            data_points.append(point)
                
                # Process simple JSON array of points
                elif isinstance(data, list):
                    for point in data:
                        if 'lat' in point and 'lng' in point:
                            data_points.append(point)
            
            elif file_path.endswith('.csv'):
                import csv
                with open(file_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'lat' in row and 'lng' in row:
                            try:
                                point = {
                                    'lat': float(row['lat']),
                                    'lng': float(row['lng']),
                                    'intensity': float(row.get('intensity', 1))
                                }
                                
                                # Create popup from other columns
                                popup = "<div>"
                                for key, value in row.items():
                                    if key not in ['lat', 'lng', 'intensity']:
                                        popup += f"<strong>{key}:</strong> {value}<br>"
                                popup += "</div>"
                                
                                if len(popup) > 11:  # More than just the div tags
                                    point['popup'] = popup
                                
                                data_points.append(point)
                            except (ValueError, KeyError):
                                continue
            
            # Update UI
            self.data_source_label.setText(os.path.basename(file_path))
            self.data_points_label.setText(str(len(data_points)))
            
            # Send data to map
            self.map_view.page().runJavaScript(
                f"loadData({json.dumps(data_points)});"
            )
            
            # Set auto-center status
            self.map_view.page().runJavaScript(
                f"document.getElementById('autoCenterEnabled').checked = {str(self.auto_center_check.isChecked()).lower()};"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Data Load Error", f"Failed to load data: {str(e)}")
    
    def clear_data(self):
        """Clear all data from the map"""
        self.map_view.page().runJavaScript("clearData();")
        self.data_source_label.setText("No data loaded")
        self.data_points_label.setText("0")
    
    def closeEvent(self, event):
        """Handle widget close event"""
        # Clean up temporary file
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
        
        super().closeEvent(event)