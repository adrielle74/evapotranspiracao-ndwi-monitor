// Application data and state management
class EvapotranspirationApp {
    constructor() {
        this.data = {
            monthly_data: [
                {"month": "Jan", "ndwi": 0.15, "ndvi": 0.45, "et": 3.2},
                {"month": "Feb", "ndwi": 0.25, "ndvi": 0.55, "et": 4.1},
                {"month": "Mar", "ndwi": 0.35, "ndvi": 0.70, "et": 5.2},
                {"month": "Apr", "ndwi": 0.30, "ndvi": 0.75, "et": 5.8},
                {"month": "May", "ndwi": 0.10, "ndvi": 0.65, "et": 4.5},
                {"month": "Jun", "ndwi": -0.05, "ndvi": 0.50, "et": 3.2},
                {"month": "Jul", "ndwi": -0.15, "ndvi": 0.35, "et": 2.1},
                {"month": "Aug", "ndwi": -0.20, "ndvi": 0.25, "et": 1.8},
                {"month": "Sep", "ndwi": -0.10, "ndvi": 0.30, "et": 2.3},
                {"month": "Oct", "ndwi": 0.05, "ndvi": 0.40, "et": 2.8},
                {"month": "Nov", "ndwi": 0.20, "ndvi": 0.50, "et": 3.5},
                {"month": "Dec", "ndwi": 0.30, "ndvi": 0.60, "et": 4.0}
            ],
            location: {
                name: "Kennedy, Bahia",
                lat: -11.0833,
                lng: -40.1667,
                area_km2: 25
            },
            statistics: {
                ndwi: {"mean": 0.098, "min": -0.20, "max": 0.35, "std": 0.186},
                ndvi: {"mean": 0.500, "min": 0.25, "max": 0.75, "std": 0.173},
                et: {"mean": 3.54, "min": 1.8, "max": 5.8, "std": 1.24}
            }
        };
        
        this.charts = {};
        this.map = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        
        // Add small delay to ensure DOM is fully ready
        setTimeout(() => {
            this.initializeMap();
            this.createCharts();
            this.updateMetrics();
            this.updateStatisticsTable();
        }, 100);
    }
    
    setupEventListeners() {
        // Buffer slider
        const bufferSlider = document.getElementById('buffer');
        const bufferValue = document.getElementById('bufferValue');
        
        if (bufferSlider && bufferValue) {
            bufferSlider.addEventListener('input', (e) => {
                bufferValue.textContent = `${e.target.value} km`;
                this.updateMapArea(parseFloat(e.target.value));
            });
        }
        
        // Process button
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => {
                this.processData();
            });
        }
        
        // Download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadCSV();
            });
        }
        
        // Coordinate inputs
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        
        if (latInput) {
            latInput.addEventListener('change', () => {
                this.updateMapLocation();
            });
        }
        
        if (lngInput) {
            lngInput.addEventListener('change', () => {
                this.updateMapLocation();
            });
        }
    }
    
    initializeMap() {
        const mapElement = document.getElementById('map');
        if (!mapElement) return;
        
        const { lat, lng } = this.data.location;
        
        this.map = L.map('map').setView([lat, lng], 10);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Add marker
        this.marker = L.marker([lat, lng]).addTo(this.map)
            .bindPopup(`<b>${this.data.location.name}</b><br/>Área de Estudo`)
            .openPopup();
        
        // Add circle to show study area
        this.circle = L.circle([lat, lng], {
            color: '#1FB8CD',
            fillColor: '#1FB8CD',
            fillOpacity: 0.2,
            radius: 5000 // 5km in meters
        }).addTo(this.map);
    }
    
    updateMapLocation() {
        const lat = parseFloat(document.getElementById('latitude').value);
        const lng = parseFloat(document.getElementById('longitude').value);
        
        if (!isNaN(lat) && !isNaN(lng) && this.map) {
            this.map.setView([lat, lng], 10);
            this.marker.setLatLng([lat, lng]);
            this.circle.setLatLng([lat, lng]);
            this.data.location.lat = lat;
            this.data.location.lng = lng;
        }
    }
    
    updateMapArea(radiusKm) {
        if (this.circle) {
            const radiusMeters = radiusKm * 1000;
            this.circle.setRadius(radiusMeters);
            this.data.location.area_km2 = Math.PI * Math.pow(radiusKm, 2);
            const currentAreaElement = document.getElementById('currentArea');
            if (currentAreaElement) {
                currentAreaElement.textContent = `${this.data.location.area_km2.toFixed(1)} km²`;
            }
        }
    }
    
    createCharts() {
        this.createTimeSeriesChart();
        // Add delay to ensure containers are ready
        setTimeout(() => {
            this.createCorrelationCharts();
        }, 200);
    }
    
    createTimeSeriesChart() {
        const ctx = document.getElementById('timeSeriesChart');
        if (!ctx) return;
        
        const months = this.data.monthly_data.map(d => d.month);
        
        this.charts.timeSeries = new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'NDWI',
                        data: this.data.monthly_data.map(d => d.ndwi),
                        borderColor: '#1FB8CD',
                        backgroundColor: '#1FB8CD',
                        fill: false,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'NDVI',
                        data: this.data.monthly_data.map(d => d.ndvi),
                        borderColor: '#22c55e',
                        backgroundColor: '#22c55e',
                        fill: false,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'ET (mm/dia)',
                        data: this.data.monthly_data.map(d => d.et),
                        borderColor: '#FFC185',
                        backgroundColor: '#FFC185',
                        fill: false,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                label += context.parsed.y.toFixed(3);
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Mês'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Índices Espectrais'
                        },
                        min: -0.3,
                        max: 0.8
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'ET (mm/dia)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        min: 0,
                        max: 7
                    }
                }
            }
        });
    }
    
    createCorrelationCharts() {
        // NDWI vs ET correlation
        const ndwiEtCtx = document.getElementById('ndwiEtChart');
        if (ndwiEtCtx) {
            this.charts.ndwiEt = new Chart(ndwiEtCtx.getContext('2d'), {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'NDWI x ET',
                        data: this.data.monthly_data.map(d => ({x: d.ndwi, y: d.et})),
                        backgroundColor: '#1FB8CD',
                        borderColor: '#1FB8CD',
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `NDWI: ${context.parsed.x.toFixed(3)}, ET: ${context.parsed.y.toFixed(1)} mm/dia`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'NDWI'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'ET (mm/dia)'
                            }
                        }
                    }
                }
            });
        }
        
        // NDVI vs ET correlation
        const ndviEtCtx = document.getElementById('ndviEtChart');
        if (ndviEtCtx) {
            this.charts.ndviEt = new Chart(ndviEtCtx.getContext('2d'), {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'NDVI x ET',
                        data: this.data.monthly_data.map(d => ({x: d.ndvi, y: d.et})),
                        backgroundColor: '#22c55e',
                        borderColor: '#22c55e',
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `NDVI: ${context.parsed.x.toFixed(3)}, ET: ${context.parsed.y.toFixed(1)} mm/dia`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'NDVI'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'ET (mm/dia)'
                            }
                        }
                    }
                }
            });
        }
    }
    
    updateMetrics() {
        const ndwiAvg = document.getElementById('ndwiAvg');
        const ndviAvg = document.getElementById('ndviAvg');
        const etAvg = document.getElementById('etAvg');
        
        if (ndwiAvg) ndwiAvg.textContent = this.data.statistics.ndwi.mean.toFixed(3);
        if (ndviAvg) ndviAvg.textContent = this.data.statistics.ndvi.mean.toFixed(3);
        if (etAvg) etAvg.textContent = this.data.statistics.et.mean.toFixed(2);
    }
    
    updateStatisticsTable() {
        const tbody = document.getElementById('statsTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        const variables = [
            { name: 'NDWI', data: this.data.statistics.ndwi },
            { name: 'NDVI', data: this.data.statistics.ndvi },
            { name: 'ET (mm/dia)', data: this.data.statistics.et }
        ];
        
        variables.forEach(variable => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${variable.name}</strong></td>
                <td>${variable.data.mean.toFixed(3)}</td>
                <td>${variable.data.min.toFixed(3)}</td>
                <td>${variable.data.max.toFixed(3)}</td>
                <td>${variable.data.std.toFixed(3)}</td>
            `;
            tbody.appendChild(row);
        });
    }
    
    processData() {
        const modal = document.getElementById('loadingModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
        
        // Simulate processing time
        setTimeout(() => {
            // Generate some variation in the data
            this.generateNewData();
            this.updateCharts();
            this.updateMetrics();
            this.updateStatisticsTable();
            
            if (modal) {
                modal.classList.add('hidden');
            }
            
            // Show success message
            this.showNotification('Dados processados com sucesso!', 'success');
        }, 2000);
    }
    
    generateNewData() {
        // Add some random variation to simulate new satellite data
        this.data.monthly_data = this.data.monthly_data.map(d => ({
            ...d,
            ndwi: d.ndwi + (Math.random() - 0.5) * 0.1,
            ndvi: d.ndvi + (Math.random() - 0.5) * 0.1,
            et: Math.max(0.5, d.et + (Math.random() - 0.5) * 0.5)
        }));
        
        // Recalculate statistics
        this.calculateStatistics();
    }
    
    calculateStatistics() {
        const ndwiValues = this.data.monthly_data.map(d => d.ndwi);
        const ndviValues = this.data.monthly_data.map(d => d.ndvi);
        const etValues = this.data.monthly_data.map(d => d.et);
        
        this.data.statistics = {
            ndwi: this.getStats(ndwiValues),
            ndvi: this.getStats(ndviValues),
            et: this.getStats(etValues)
        };
    }
    
    getStats(values) {
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const min = Math.min(...values);
        const max = Math.max(...values);
        const variance = values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
        const std = Math.sqrt(variance);
        
        return { mean, min, max, std };
    }
    
    updateCharts() {
        // Update time series chart
        if (this.charts.timeSeries) {
            this.charts.timeSeries.data.datasets[0].data = this.data.monthly_data.map(d => d.ndwi);
            this.charts.timeSeries.data.datasets[1].data = this.data.monthly_data.map(d => d.ndvi);
            this.charts.timeSeries.data.datasets[2].data = this.data.monthly_data.map(d => d.et);
            this.charts.timeSeries.update();
        }
        
        // Update correlation charts
        if (this.charts.ndwiEt) {
            this.charts.ndwiEt.data.datasets[0].data = this.data.monthly_data.map(d => ({x: d.ndwi, y: d.et}));
            this.charts.ndwiEt.update();
        }
        
        if (this.charts.ndviEt) {
            this.charts.ndviEt.data.datasets[0].data = this.data.monthly_data.map(d => ({x: d.ndvi, y: d.et}));
            this.charts.ndviEt.update();
        }
    }
    
    downloadCSV() {
        try {
            // Create CSV header
            let csv = 'Mês,NDWI,NDVI,ET (mm/dia)\n';
            
            // Add data rows
            this.data.monthly_data.forEach(d => {
                csv += `${d.month},${d.ndwi.toFixed(4)},${d.ndvi.toFixed(4)},${d.et.toFixed(2)}\n`;
            });
            
            // Create blob and download
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            
            if (link.download !== undefined) {
                // Use HTML5 download attribute
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', 'dados_evapotranspiracao.csv');
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                
                this.showNotification('Arquivo CSV baixado com sucesso!', 'success');
            } else {
                // Fallback for older browsers
                this.showNotification('Download não suportado neste navegador', 'error');
            }
        } catch (error) {
            console.error('Erro no download:', error);
            this.showNotification('Erro ao baixar arquivo CSV', 'error');
        }
    }
    
    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(n => n.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#1FB8CD'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
        `;
        
        // Add animation keyframes
        if (!document.querySelector('style[data-notifications]')) {
            const style = document.createElement('style');
            style.setAttribute('data-notifications', '');
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EvapotranspirationApp();
});