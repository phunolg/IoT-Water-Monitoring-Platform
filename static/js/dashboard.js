class WaterMonitoringDashboard {
    constructor() {
        this.charts = {};
        this.refreshInterval = 10000;
        this.refreshTimer = null;
        this.isRefreshing = false;

        this.init();
    }

    init() {
        console.log('Initializing Water Monitoring Dashboard...');
        this.initializeCharts();
        this.loadInitialData();
        this.startAutoRefresh();
        this.setupEventListeners();
        console.log('Dashboard initialized successfully');
    }

    initializeCharts() {
        const phCtx = document.getElementById('phChart');
        if (phCtx) {
            this.charts.ph = new Chart(phCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'pH Level',
                        data: [],
                        borderColor: '#2196F3',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('pH Level', 'pH', 0, 14)
            });
        }

        const tdsCtx = document.getElementById('tdsChart');
        if (tdsCtx) {
            this.charts.tds = new Chart(tdsCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'TDS (ppm)',
                        data: [],
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('TDS Level', 'ppm', 0, 1000)
            });
        }

        // NTU Chart
        const ntuCtx = document.getElementById('ntuChart');
        if (ntuCtx) {
            this.charts.ntu = new Chart(ntuCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'NTU',
                        data: [],
                        borderColor: '#FF9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions('Turbidity Level', 'NTU', 0, 100)
            });
        }

        // Combined Chart
        const combinedCtx = document.getElementById('combinedChart');
        if (combinedCtx) {
            this.charts.combined = new Chart(combinedCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'pH',
                            data: [],
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.1)',
                            yAxisID: 'y',
                        },
                        {
                            label: 'TDS (ppm)',
                            data: [],
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            yAxisID: 'y1',
                        },
                        {
                            label: 'NTU',
                            data: [],
                            borderColor: '#FF9800',
                            backgroundColor: 'rgba(255, 152, 0, 0.1)',
                            yAxisID: 'y2',
                        }
                    ]
                },
                options: this.getCombinedChartOptions()
            });
        }
    }

    getChartOptions(title, yAxisLabel, min, max) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: yAxisLabel
                    },
                    min: min,
                    max: max
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        };
    }

    getCombinedChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                title: {
                    display: true,
                    text: 'All Water Quality Parameters',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'pH'
                    },
                    min: 0,
                    max: 14
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'TDS (ppm)'
                    },
                    min: 0,
                    max: 1000,
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                y2: {
                    type: 'linear',
                    display: false,
                    min: 0,
                    max: 100
                }
            }
        };
    }

    async loadInitialData() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/readings/?limit=50');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.updateChartsWithData(data.results || data);
            this.updateStatsCards(data.results || data);
            this.updateDataTable(data.results || data);
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load initial data');
        } finally {
            this.showLoading(false);
        }
    }

    async refreshData() {
        if (this.isRefreshing) return;
        
        try {
            this.isRefreshing = true;
            
            const response = await fetch('/api/readings/?limit=50');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.updateChartsWithData(data.results || data);
            this.updateStatsCards(data.results || data);
            this.updateDataTable(data.results || data);
            
            // Show success indicator
            this.showRefreshSuccess();
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showError('Failed to refresh data');
        } finally {
            this.isRefreshing = false;
        }
    }

    updateChartsWithData(readings) {
        if (!readings || readings.length === 0) return;

        // Sort readings by timestamp
        const sortedReadings = readings.sort((a, b) => 
            new Date(a.timestamp) - new Date(b.timestamp)
        );

        // Get the latest 20 readings for charts
        const latestReadings = sortedReadings.slice(-20);

        // Prepare data for charts
        const labels = latestReadings.map(reading => 
            new Date(reading.timestamp).toLocaleTimeString()
        );
        const phData = latestReadings.map(reading => reading.ph_value);
        const tdsData = latestReadings.map(reading => reading.tds_value);
        const ntuData = latestReadings.map(reading => reading.ntu_value);

        // Update individual charts
        if (this.charts.ph) {
            this.charts.ph.data.labels = labels;
            this.charts.ph.data.datasets[0].data = phData;
            this.charts.ph.update('none');
        }

        if (this.charts.tds) {
            this.charts.tds.data.labels = labels;
            this.charts.tds.data.datasets[0].data = tdsData;
            this.charts.tds.update('none');
        }

        if (this.charts.ntu) {
            this.charts.ntu.data.labels = labels;
            this.charts.ntu.data.datasets[0].data = ntuData;
            this.charts.ntu.update('none');
        }

        // Update combined chart
        if (this.charts.combined) {
            this.charts.combined.data.labels = labels;
            this.charts.combined.data.datasets[0].data = phData;
            this.charts.combined.data.datasets[1].data = tdsData;
            this.charts.combined.data.datasets[2].data = ntuData;
            this.charts.combined.update('none');
        }
    }

    updateStatsCards(readings) {
        if (!readings || readings.length === 0) return;

        const latestReading = readings[0];

        // Update pH card
        const phValue = document.getElementById('ph-value');
        const phStatus = document.getElementById('ph-status');
        if (phValue && latestReading.ph_value !== undefined) {
            phValue.textContent = latestReading.ph_value.toFixed(1);
            if (phStatus) {
                phStatus.textContent = this.getPhStatus(latestReading.ph_value);
                phStatus.className = `status-badge ${this.getStatusClass(latestReading.ph_value, 'ph')}`;
            }
        }

        // Update TDS card
        const tdsValue = document.getElementById('tds-value');
        const tdsStatus = document.getElementById('tds-status');
        if (tdsValue && latestReading.tds_value !== undefined) {
            tdsValue.textContent = Math.round(latestReading.tds_value);
            if (tdsStatus) {
                tdsStatus.textContent = this.getTdsStatus(latestReading.tds_value);
                tdsStatus.className = `status-badge ${this.getStatusClass(latestReading.tds_value, 'tds')}`;
            }
        }

        // Update NTU card
        const ntuValue = document.getElementById('ntu-value');
        const ntuStatus = document.getElementById('ntu-status');
        if (ntuValue && latestReading.ntu_value !== undefined) {
            ntuValue.textContent = latestReading.ntu_value.toFixed(1);
            if (ntuStatus) {
                ntuStatus.textContent = this.getNtuStatus(latestReading.ntu_value);
                ntuStatus.className = `status-badge ${this.getStatusClass(latestReading.ntu_value, 'ntu')}`;
            }
        }

        // Update last updated time
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = new Date().toLocaleString();
        }
    }

    updateDataTable(readings) {
        const tableBody = document.getElementById('readings-table-body');
        if (!tableBody || !readings) return;

        // Clear existing rows
        tableBody.innerHTML = '';

        // Add new rows (latest 10 readings)
        const latestReadings = readings.slice(0, 10);
        latestReadings.forEach(reading => {
            const row = document.createElement('tr');
            row.className = 'data-refresh';
            row.innerHTML = `
                <td>${new Date(reading.timestamp).toLocaleString()}</td>
                <td>${reading.ph_value ? reading.ph_value.toFixed(1) : 'N/A'}</td>
                <td>${reading.tds_value ? Math.round(reading.tds_value) : 'N/A'}</td>
                <td>${reading.ntu_value ? reading.ntu_value.toFixed(1) : 'N/A'}</td>
                <td>
                    <span class="status-indicator status-online"></span>
                    Online
                </td>
            `;
            tableBody.appendChild(row);
        });
    }

    getPhStatus(value) {
        if (value >= 6.5 && value <= 8.5) return 'Excellent';
        if (value >= 6.0 && value <= 9.0) return 'Good';
        if (value >= 5.5 && value <= 9.5) return 'Fair';
        return 'Poor';
    }

    getTdsStatus(value) {
        if (value <= 300) return 'Excellent';
        if (value <= 600) return 'Good';
        if (value <= 900) return 'Fair';
        return 'Poor';
    }

    getNtuStatus(value) {
        if (value <= 1) return 'Excellent';
        if (value <= 4) return 'Good';
        if (value <= 10) return 'Fair';
        return 'Poor';
    }

    getStatusClass(value, type) {
        let status;
        switch (type) {
            case 'ph':
                status = this.getPhStatus(value);
                break;
            case 'tds':
                status = this.getTdsStatus(value);
                break;
            case 'ntu':
                status = this.getNtuStatus(value);
                break;
            default:
                return 'status-good';
        }

        switch (status) {
            case 'Excellent': return 'status-excellent';
            case 'Good': return 'status-good';
            case 'Fair': return 'status-warning';
            case 'Poor': return 'status-danger';
            default: return 'status-good';
        }
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    setupEventListeners() {
        // Manual refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // Auto refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }

        // Export data button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }
    }

    showLoading(show) {
        const loadingElements = document.querySelectorAll('.loading-spinner');
        loadingElements.forEach(element => {
            element.style.display = show ? 'inline-block' : 'none';
        });
    }

    showError(message) {
        let alertDiv = document.getElementById('error-alert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.id = 'error-alert';
            alertDiv.className = 'alert alert-danger';
            
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
            }
        }
        
        alertDiv.innerHTML = `
            <span class="alert-icon">⚠️</span>
            ${message}
        `;
        alertDiv.style.display = 'flex';
        
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 5000);
    }

    showRefreshSuccess() {
        const successIndicator = document.createElement('div');
        successIndicator.className = 'alert alert-success';
        successIndicator.innerHTML = `
            <span class="alert-icon">✅</span>
            Data refreshed successfully
        `;
        successIndicator.style.position = 'fixed';
        successIndicator.style.top = '20px';
        successIndicator.style.right = '20px';
        successIndicator.style.zIndex = '9999';
        successIndicator.style.minWidth = '250px';
        
        document.body.appendChild(successIndicator);
        
        setTimeout(() => {
            document.body.removeChild(successIndicator);
        }, 3000);
    }

    async exportData() {
        try {
            const response = await fetch('/api/readings/?format=csv');
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `water_readings_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export error:', error);
            this.showError('Failed to export data');
        }
    }

    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        this.stopAutoRefresh();
    }
}

const dashboard = new WaterMonitoringDashboard();

window.waterDashboard = dashboard;