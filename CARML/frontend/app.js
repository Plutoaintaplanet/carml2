// CarML Frontend Application Logic

// API Base URL
const API_BASE = "";

// Global Application State
let appState = {
    activeTab: "tab-search",
    cars: [],
    selectedCar: null,
    selectedCompareCars: [], // Array of cars checked for comparison
    forecastChart: null,
    stats: null,
    modelInfo: null
};

// DOM Elements
const dom = {
    navBtns: document.querySelectorAll('.nav-btn'),
    tabPanes: document.querySelectorAll('.tab-pane'),
    
    // Stats
    statRecords: document.querySelector('#stat-records .stat-value'),
    statAvgPrice: document.querySelector('#stat-avg-price .stat-value'),
    statAvgKms: document.querySelector('#stat-avg-kms .stat-value'),
    statModels: document.querySelector('#stat-models .stat-value'),
    
    // Search Filters
    filterSearch: document.getElementById('filter-search'),
    filterMinPrice: document.getElementById('filter-min-price'),
    filterMaxPrice: document.getElementById('filter-max-price'),
    filterFuel: document.getElementById('filter-fuel'),
    filterTransmission: document.getElementById('filter-transmission'),
    btnResetFilters: document.getElementById('btn-reset-filters'),
    resultsCount: document.getElementById('results-count'),
    carsList: document.getElementById('cars-list'),
    
    // Multi-Select Comparison Actions
    btnCompareSelected: document.getElementById('btn-compare-selected'),
    compareCount: document.getElementById('compare-count'),
    conclusionBox: document.getElementById('conclusion-box'),
    conclusionText: document.getElementById('conclusion-text'),
    
    // Forecast Panel
    forecastPanel: document.getElementById('forecast-panel'),
    btnCloseForecast: document.getElementById('btn-close-forecast'),
    forecastCarName: document.getElementById('forecast-car-name'),
    specYear: document.getElementById('spec-year'),
    specKms: document.getElementById('spec-kms'),
    specFuel: document.getElementById('spec-fuel'),
    specTransmission: document.getElementById('spec-transmission'),
    specPresentPrice: document.getElementById('spec-present-price'),
    specSellingPrice: document.getElementById('spec-selling-price'),
    specDepreciation: document.getElementById('spec-depreciation'),
    forecastAnnualRun: document.getElementById('forecast-annual-run'),
    forecastRunVal: document.getElementById('forecast-run-val'),
    btnGenerateForecast: document.getElementById('btn-generate-forecast'),
    forecastTableBody: document.getElementById('forecast-table-body'),
    chartCanvas: document.getElementById('forecastChart'),
    
    // Estimator
    estimatorForm: document.getElementById('estimator-form'),
    estCarName: document.getElementById('est-car-name'),
    estPresentPrice: document.getElementById('est-present-price'),
    estKms: document.getElementById('est-kms'),
    estYear: document.getElementById('est-year'),
    estFuel: document.getElementById('est-fuel'),
    estTransmission: document.getElementById('est-transmission'),
    estSeller: document.getElementById('est-seller'),
    estOwner: document.getElementById('est-owner'),
    carDatalist: document.getElementById('car-name-datalist'),
    estimatorResultEmpty: document.getElementById('estimator-result-empty'),
    estimatorResultContent: document.getElementById('estimator-result-content'),
    resultCarTitle: document.getElementById('result-car-title'),
    resultSellingPrice: document.getElementById('result-selling-price'),
    resultPresentPrice: document.getElementById('result-present-price'),
    resultDepreciation: document.getElementById('result-depreciation'),
    resultRetainedPct: document.getElementById('result-retained-pct'),
    resultAge: document.getElementById('result-age'),
    
    // Insights
    modelAlgoName: document.getElementById('model-algo-name'),
    modelR2: document.getElementById('model-r2'),
    modelMae: document.getElementById('model-mae'),
    catFeaturesList: document.getElementById('cat-features-list'),
    numFeaturesList: document.getElementById('num-features-list'),
    btnRetrain: document.getElementById('btn-retrain-model'),
    retrainConsole: document.getElementById('retrain-log-console')
};

// Startup Initializations
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadStats();
    loadModelInfo();
    loadCars();
    
    // Set default estimator year to current year
    if (dom.estYear) {
        dom.estYear.value = 2025;
    }
    
    // Search event listeners (with debounce)
    let searchTimeout;
    const triggerSearch = () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(loadCars, 300);
    };
    
    dom.filterSearch.addEventListener('input', triggerSearch);
    dom.filterMinPrice.addEventListener('input', triggerSearch);
    dom.filterMaxPrice.addEventListener('input', triggerSearch);
    dom.filterFuel.addEventListener('change', loadCars);
    dom.filterTransmission.addEventListener('change', loadCars);
    
    dom.btnResetFilters.addEventListener('click', resetFilters);
    
    // Forecast elements
    dom.btnCloseForecast.addEventListener('click', () => {
        dom.forecastPanel.classList.add('hidden');
        appState.selectedCar = null;
        clearCompareSelection();
    });
    
    dom.forecastAnnualRun.addEventListener('input', (e) => {
        const val = parseInt(e.target.value).toLocaleString();
        dom.forecastRunVal.textContent = val;
    });
    
    dom.btnGenerateForecast.addEventListener('click', fetchForecast);
    
    // Compare selected button
    dom.btnCompareSelected.addEventListener('click', compareSelectedCars);
    
    // Estimator submit
    dom.estimatorForm.addEventListener('submit', handleEstimate);
    
    // Retrain action
    dom.btnRetrain.addEventListener('click', handleRetrain);
});

// Sidebar Tab switching logic
function initTabs() {
    dom.navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.target;
            
            // Toggle sidebar buttons
            dom.navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle tabs
            dom.tabPanes.forEach(pane => {
                pane.classList.remove('active');
                if (pane.id === target) {
                    pane.classList.add('active');
                }
            });
            
            appState.activeTab = target;
        });
    });
}

// Fetch Global Statistics
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        if (!res.ok) throw new Error("Stats request failed");
        const data = await res.json();
        appState.stats = data;
        
        // Populate stats dashboard cards with animation
        animateValue(dom.statRecords, 0, data.total_records, 1000);
        animateValue(dom.statAvgPrice, 0, data.avg_selling_price, 1000, " Lakhs");
        animateValue(dom.statAvgKms, 0, data.avg_kms_driven, 1000, " km", true);
        animateValue(dom.statModels, 0, data.unique_cars_count, 1000);
        
        // Populate datalist in custom estimator
        dom.carDatalist.innerHTML = "";
        data.unique_cars.forEach(car => {
            const opt = document.createElement('option');
            opt.value = car;
            dom.carDatalist.appendChild(opt);
        });
        
    } catch (err) {
        console.error("Error loading stats:", err);
    }
}

// Fetch Model Details
async function loadModelInfo() {
    try {
        const res = await fetch(`${API_BASE}/api/model_info`);
        if (!res.ok) throw new Error("Model info failed");
        const data = await res.json();
        appState.modelInfo = data;
        
        // Populate insights pane
        dom.modelAlgoName.textContent = data.algorithm;
        dom.modelR2.textContent = data.metrics.r2_score.toFixed(3);
        dom.modelMae.textContent = data.metrics.mae.toFixed(3);
        
        // Populate feature lists
        dom.catFeaturesList.innerHTML = "";
        data.features.categorical.forEach(f => {
            const span = document.createElement('span');
            span.textContent = f;
            dom.catFeaturesList.appendChild(span);
        });
        
        dom.numFeaturesList.innerHTML = "";
        data.features.numerical.forEach(f => {
            const span = document.createElement('span');
            span.textContent = f;
            dom.numFeaturesList.appendChild(span);
        });
        
    } catch (err) {
        console.error("Error loading model info:", err);
    }
}

// Fetch Vehicle List with current filters
async function loadCars() {
    dom.carsList.innerHTML = `
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Filtering car catalog...</p>
        </div>
    `;
    
    // Clear selection on new search
    clearCompareSelection();
    
    const queryParams = new URLSearchParams();
    if (dom.filterSearch.value) queryParams.append("search", dom.filterSearch.value.trim());
    if (dom.filterMinPrice.value) queryParams.append("min_price", dom.filterMinPrice.value);
    if (dom.filterMaxPrice.value) queryParams.append("max_price", dom.filterMaxPrice.value);
    if (dom.filterFuel.value) queryParams.append("fuel_type", dom.filterFuel.value);
    if (dom.filterTransmission.value) queryParams.append("transmission", dom.filterTransmission.value);
    
    try {
        const res = await fetch(`${API_BASE}/api/cars?${queryParams.toString()}`);
        if (!res.ok) throw new Error("Search request failed");
        const cars = await res.json();
        appState.cars = cars;
        
        dom.resultsCount.textContent = `${cars.length} found`;
        
        renderCarsGrid(cars);
        
    } catch (err) {
        dom.carsList.innerHTML = `
            <div class="loading-state">
                <i data-lucide="alert-circle" style="color: var(--color-danger); width: 32px; height: 32px;"></i>
                <p>Failed to query the database. Check API server status.</p>
            </div>
        `;
        lucide.createIcons();
        console.error("Error loading cars:", err);
    }
}

// Reset Filters
function resetFilters() {
    dom.filterSearch.value = "";
    dom.filterMinPrice.value = "";
    dom.filterMaxPrice.value = "";
    dom.filterFuel.value = "All";
    dom.filterTransmission.value = "All";
    loadCars();
}

// Clear selected cars compare list
function clearCompareSelection() {
    appState.selectedCompareCars = [];
    dom.btnCompareSelected.classList.add('hidden');
    
    // Uncheck UI checkboxes
    document.querySelectorAll('.car-compare-check').forEach(chk => chk.checked = false);
}

// Render dynamic list of cars
function renderCarsGrid(cars) {
    if (cars.length === 0) {
        dom.carsList.innerHTML = `
            <div class="loading-state">
                <i data-lucide="help-circle" style="color: var(--text-dim); width: 32px; height: 32px;"></i>
                <p>No matching vehicles found. Try adjusting filters.</p>
            </div>
        `;
        lucide.createIcons();
        return;
    }
    
    dom.carsList.innerHTML = "";
    
    // Render up to 50 cars for UI performance
    const renderLimit = cars.slice(0, 50);
    
    renderLimit.forEach((car, index) => {
        const card = document.createElement('div');
        card.className = "car-card";
        
        card.innerHTML = `
            <div class="car-card-header" style="position: relative; padding-left: 26px;">
                <div class="car-card-checkbox-wrapper" style="position: absolute; top: 3px; left: 0; z-index: 10;">
                    <input type="checkbox" class="car-compare-check" data-index="${index}" style="width: 16px; height: 16px; accent-color: var(--color-primary); cursor: pointer;">
                </div>
                <div class="car-card-title" title="${car.Car_Name}">${car.Car_Name}</div>
                <div class="car-card-year" style="margin-left: auto;">${car.Year}</div>
            </div>
            <div class="car-card-price" style="padding-left: 26px;">${car.Selling_Price.toFixed(2)}<span>Lakhs</span></div>
            
            <div class="car-card-details" style="padding-left: 26px;">
                <div class="detail-item">
                    <i data-lucide="navigation"></i>
                    <span>${car.Kms_Driven.toLocaleString()} km</span>
                </div>
                <div class="detail-item">
                    <i data-lucide="settings"></i>
                    <span>${car.Transmission}</span>
                </div>
                <div class="detail-item">
                    <i data-lucide="tag"></i>
                    <span>${car.Fuel_Type}</span>
                </div>
                <div class="detail-item">
                    <i data-lucide="user"></i>
                    <span>Owner: ${car.Owner}</span>
                </div>
            </div>
            
            <button class="btn-primary select-car-btn" data-index="${index}">
                <i data-lucide="trending-down"></i>
                <span>Forecast Depreciation</span>
            </button>
        `;
        
        dom.carsList.appendChild(card);
    });
    
    // Bind click events on Forecast buttons
    dom.carsList.querySelectorAll('.select-car-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const btnEl = e.currentTarget;
            const idx = parseInt(btnEl.dataset.index);
            clearCompareSelection();
            selectCarForForecast(cars[idx]);
        });
    });
    
    // Bind checkbox compare change events
    dom.carsList.querySelectorAll('.car-compare-check').forEach(chk => {
        chk.addEventListener('change', (e) => {
            const idx = parseInt(e.target.dataset.index);
            const car = cars[idx];
            
            if (e.target.checked) {
                // Ensure car is not already added
                if (!appState.selectedCompareCars.some(c => c.Car_Name === car.Car_Name && c.Selling_Price === car.Selling_Price && c.Kms_Driven === car.Kms_Driven)) {
                    appState.selectedCompareCars.push(car);
                }
            } else {
                appState.selectedCompareCars = appState.selectedCompareCars.filter(
                    c => !(c.Car_Name === car.Car_Name && c.Selling_Price === car.Selling_Price && c.Kms_Driven === car.Kms_Driven)
                );
            }
            
            updateCompareButton();
        });
    });
    
    lucide.createIcons();
}

// Update "Compare & Conclude" Action Button
function updateCompareButton() {
    const count = appState.selectedCompareCars.length;
    if (count > 0) {
        dom.btnCompareSelected.classList.remove('hidden');
        dom.compareCount.textContent = count;
    } else {
        dom.btnCompareSelected.classList.add('hidden');
    }
}

// Select a single car and populate details
function selectCarForForecast(car) {
    appState.selectedCar = car;
    
    const age = 2025 - car.Year;
    const dep = car.Present_Price - car.Selling_Price;
    
    dom.forecastCarName.textContent = car.Car_Name;
    dom.specYear.textContent = car.Year;
    dom.specKms.textContent = car.Kms_Driven.toLocaleString();
    dom.specFuel.textContent = car.Fuel_Type;
    dom.specTransmission.textContent = car.Transmission;
    
    dom.specPresentPrice.textContent = `${car.Present_Price.toFixed(2)} L`;
    dom.specSellingPrice.textContent = `${car.Selling_Price.toFixed(2)} L`;
    dom.specDepreciation.textContent = `${dep.toFixed(2)} L`;
    
    // Reveal single car details UI
    document.querySelector('.selected-car-specs').classList.remove('hidden');
    document.querySelector('.price-summary-box').classList.remove('hidden');
    dom.conclusionBox.classList.add('hidden');
    
    // Reset forecast table head structure to single car headers
    const thead = document.querySelector('.forecast-table thead');
    thead.innerHTML = `
        <tr>
            <th>Year</th>
            <th>Car Age</th>
            <th>Cumulative KMs</th>
            <th>Predicted Depreciation (Lakhs)</th>
            <th>Estimated Resale Value (Lakhs)</th>
            <th>Retained Value (%)</th>
        </tr>
    `;
    
    // Reveal forecast panel
    dom.forecastPanel.classList.remove('hidden');
    
    // Scroll smoothly to forecast panel
    dom.forecastPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Trigger forecast computation
    fetchForecast();
}

// Fetch forecast from API
async function fetchForecast() {
    // If in comparison mode, redirect update trigger to comparative evaluation
    if (appState.selectedCompareCars.length > 0) {
        compareSelectedCars();
        return;
    }
    
    if (!appState.selectedCar) return;
    
    const car = appState.selectedCar;
    const annualRunning = parseFloat(dom.forecastAnnualRun.value);
    
    const carAge = 2025 - car.Year;
    
    const reqBody = {
        Car_Name: car.Car_Name,
        Present_Price: car.Present_Price,
        Kms_Driven: car.Kms_Driven,
        Fuel_Type: car.Fuel_Type,
        Seller_Type: car.Seller_Type,
        Transmission: car.Transmission,
        Owner: car.Owner,
        Car_Age: carAge,
        Annual_Running: annualRunning
    };
    
    try {
        dom.btnGenerateForecast.disabled = true;
        dom.btnGenerateForecast.innerHTML = `<div class="spinner" style="width: 14px; height: 14px;"></div> <span>Calculating...</span>`;
        
        const res = await fetch(`${API_BASE}/api/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqBody)
        });
        
        if (!res.ok) throw new Error("Forecast API error");
        const data = await res.json();
        
        renderForecast(data.forecast, car.Present_Price, car.Selling_Price);
        
    } catch (err) {
        console.error("Forecast error:", err);
        alert("Failed to compute forecast. Please check API server.");
    } finally {
        dom.btnGenerateForecast.disabled = false;
        dom.btnGenerateForecast.innerHTML = `<i data-lucide="trending-down"></i> <span>Update 5-Year Forecast</span>`;
        lucide.createIcons();
    }
}

// Render forecast table and chart for SINGLE vehicle
function renderForecast(forecast, originalPrice, currentPrice) {
    // 1. Render Table
    dom.forecastTableBody.innerHTML = "";
    
    // Row 0: Present Value
    const baseRow = document.createElement('tr');
    baseRow.innerHTML = `
        <td>Present</td>
        <td>${appState.selectedCar.Car_Age || (2025 - appState.selectedCar.Year)} yrs</td>
        <td class="hl-kms">${appState.selectedCar.Kms_Driven.toLocaleString()} km</td>
        <td class="hl-dep">${(originalPrice - currentPrice).toFixed(2)} Lakhs</td>
        <td class="hl-val">${currentPrice.toFixed(2)} Lakhs</td>
        <td><span class="hl-pct">${(currentPrice / originalPrice * 100).toFixed(1)}%</span></td>
    `;
    dom.forecastTableBody.appendChild(baseRow);
    
    // Future Rows
    forecast.forEach(item => {
        const tr = document.createElement('tr');
        const retainedPct = (item.estimated_value / originalPrice * 100).toFixed(1);
        
        tr.innerHTML = `
            <td>Year ${item.year}</td>
            <td>${item.age} yrs</td>
            <td class="hl-kms">${item.kms.toLocaleString()} km</td>
            <td class="hl-dep">${item.predicted_depreciation.toFixed(2)} Lakhs</td>
            <td class="hl-val">${item.estimated_value.toFixed(2)} Lakhs</td>
            <td><span class="hl-pct" style="opacity: ${Math.max(0.4, item.estimated_value / originalPrice)}">${retainedPct}%</span></td>
        `;
        dom.forecastTableBody.appendChild(tr);
    });
    
    // 2. Render Chart (Chart.js)
    if (appState.forecastChart) {
        appState.forecastChart.destroy();
    }
    
    const labels = ["Present", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"];
    const valueData = [currentPrice, ...forecast.map(i => i.estimated_value)];
    const kmsData = [appState.selectedCar.Kms_Driven, ...forecast.map(i => i.kms)];
    
    const ctx = dom.chartCanvas.getContext('2d');
    
    // Gradient fill (Rosso Corsa Red theme)
    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(213, 0, 0, 0.35)');
    gradient.addColorStop(1, 'rgba(213, 0, 0, 0.00)');
    
    appState.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Est. Value (Lakhs)',
                    data: valueData,
                    borderColor: '#d50000',
                    borderWidth: 3,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: '#ff1744',
                    pointBorderColor: '#ffffff',
                    pointHoverRadius: 8,
                    pointRadius: 5,
                    yAxisID: 'y'
                }
            ]
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
                            const index = context.dataIndex;
                            return ` Value: ${valueData[index].toFixed(2)} Lakhs (${kmsData[index].toLocaleString()} km)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Outfit'
                        }
                    },
                    min: 0
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Outfit'
                        }
                    }
                }
            }
        }
    });
}

// Compare Selected Cars & Render Conclusion
async function compareSelectedCars() {
    if (appState.selectedCompareCars.length === 0) return;
    
    dom.forecastCarName.textContent = "Comparative Analytics Verdict";
    
    // Hide single car details specs column
    document.querySelector('.selected-car-specs').classList.add('hidden');
    document.querySelector('.price-summary-box').classList.add('hidden');
    
    // Setup comparison table headers
    const thead = document.querySelector('.forecast-table thead');
    thead.innerHTML = `
        <tr>
            <th>Vehicle Model</th>
            <th>Purchase Year</th>
            <th>Showroom Price</th>
            <th>Current Value</th>
            <th>Est. Year 1 Value</th>
            <th>Est. Year 3 Value</th>
            <th>Est. Year 5 Value</th>
            <th>Year 5 Retained %</th>
            <th>Decision Verdict</th>
        </tr>
    `;
    
    const annualRunning = parseFloat(dom.forecastAnnualRun.value);
    
    // Query forecasting APIs in parallel
    const forecastPromises = appState.selectedCompareCars.map(async (car) => {
        const carAge = 2025 - car.Year;
        const reqBody = {
            Car_Name: car.Car_Name,
            Present_Price: car.Present_Price,
            Kms_Driven: car.Kms_Driven,
            Fuel_Type: car.Fuel_Type,
            Seller_Type: car.Seller_Type,
            Transmission: car.Transmission,
            Owner: car.Owner,
            Car_Age: carAge,
            Annual_Running: annualRunning
        };
        
        const res = await fetch(`${API_BASE}/api/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqBody)
        });
        
        if (!res.ok) throw new Error(`Forecast failed for ${car.Car_Name}`);
        const data = await res.json();
        return { car, forecast: data.forecast };
    });
    
    try {
        dom.btnCompareSelected.disabled = true;
        dom.btnCompareSelected.innerHTML = `<div class="spinner" style="width: 14px; height: 14px;"></div> <span>Processing Verdict...</span>`;
        
        const results = await Promise.all(forecastPromises);
        
        // Render comparison view
        renderComparison(results);
        
        // Reveal compare dashboard
        dom.forecastPanel.classList.remove('hidden');
        dom.forecastPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (err) {
        console.error("Comparison error:", err);
        alert("Failed to compare selected vehicles. Please check server.");
    } finally {
        dom.btnCompareSelected.disabled = false;
        dom.btnCompareSelected.innerHTML = `<i data-lucide="award"></i> <span>Conclude & Compare (<span id="compare-count">${appState.selectedCompareCars.length}</span>)</span>`;
        lucide.createIcons();
    }
}

// Render comparative table, chart, and expert conclusion
function renderComparison(results) {
    // 1. Populate Table
    dom.forecastTableBody.innerHTML = "";
    
    // Sort logic to determine best picks
    // Let's copy results and calculate retained percentages
    const scoredResults = results.map(r => {
        const yr5 = r.forecast[4].estimated_value;
        const retainedPct = (yr5 / r.car.Present_Price) * 100;
        return {
            ...r,
            retainedPct: retainedPct,
            yr1: r.forecast[0].estimated_value,
            yr3: r.forecast[2].estimated_value,
            yr5: yr5
        };
    });
    
    // Top financial choice (highest retained value %)
    const bestValue = [...scoredResults].sort((a, b) => b.retainedPct - a.retainedPct)[0];
    // Lowest mileage (least engine wear)
    const lowestKms = [...scoredResults].sort((a, b) => a.car.Kms_Driven - b.car.Kms_Driven)[0];
    // Lowest entry price (budget option)
    const cheapestPrice = [...scoredResults].sort((a, b) => a.car.Selling_Price - b.car.Selling_Price)[0];
    
    scoredResults.forEach(r => {
        const tr = document.createElement('tr');
        
        // Compute Verdict Tag
        let tagHtml = "";
        if (r.car.Car_Name === bestValue.car.Car_Name && r.car.Selling_Price === bestValue.car.Selling_Price) {
            tagHtml = `<span class="hl-pct">⭐ Best Value</span>`;
        } else if (r.car.Car_Name === lowestKms.car.Car_Name && r.car.Kms_Driven === lowestKms.car.Kms_Driven) {
            tagHtml = `<span class="hl-pct" style="background: rgba(0, 229, 255, 0.08); border-color: rgba(0, 229, 255, 0.2); color: #00e5ff;">⚙️ Low Wear</span>`;
        } else if (r.car.Car_Name === cheapestPrice.car.Car_Name && r.car.Selling_Price === cheapestPrice.car.Selling_Price) {
            tagHtml = `<span class="hl-pct" style="background: rgba(255, 214, 0, 0.08); border-color: rgba(255, 214, 0, 0.2); color: #ffd600;">🪙 Budget Pick</span>`;
        } else {
            tagHtml = `<span class="hl-pct" style="background: rgba(255,255,255,0.03); border-color: rgba(255,255,255,0.08); color: var(--text-muted);">Alternative</span>`;
        }
        
        tr.innerHTML = `
            <td style="text-transform: capitalize; font-weight: 700; color: #fff;">${r.car.Car_Name}</td>
            <td>${r.car.Year}</td>
            <td>${r.car.Present_Price.toFixed(2)} L</td>
            <td class="hl-val">${r.car.Selling_Price.toFixed(2)} L</td>
            <td>${r.yr1.toFixed(2)} L</td>
            <td>${r.yr3.toFixed(2)} L</td>
            <td class="hl-val">${r.yr5.toFixed(2)} L</td>
            <td><span class="hl-pct">${r.retainedPct.toFixed(1)}%</span></td>
            <td>${tagHtml}</td>
        `;
        dom.forecastTableBody.appendChild(tr);
    });
    
    // 2. Generate expert conclusion text
    let conclusionHtml = `
        <p style="margin-bottom: 0.75rem;">Based on your selected set of <strong>${results.length}</strong> vehicles, the CarML analytics engine has compiled its market-forecast verdict:</p>
        <ul style="list-style-type: none; display: flex; flex-direction: column; gap: 0.5rem; padding-left: 0;">
            <li style="display: flex; gap: 0.5rem; align-items: flex-start;">
                <span style="color: var(--color-primary); font-weight: bold; font-family: var(--font-mono);">[FINANCE]</span>
                <span><strong>${bestValue.car.Car_Name}</strong> (${bestValue.car.Year}) is your <strong>Top Value Winner</strong>. Over a 5-year outlook, it is projected to retain the highest percentage of its showroom price at <strong>${bestValue.retainedPct.toFixed(1)}%</strong>, showcasing the slowest depreciation rate.</span>
            </li>
            <li style="display: flex; gap: 0.5rem; align-items: flex-start;">
                <span style="color: #00e5ff; font-weight: bold; font-family: var(--font-mono);">[RELIABILITY]</span>
                <span><strong>${lowestKms.car.Car_Name}</strong> (${lowestKms.car.Year}) offers the <strong>Lowest Mechanical Wear</strong>, with only <strong>${lowestKms.car.Kms_Driven.toLocaleString()} km</strong> on the odometer, making it the safest option for longevity.</span>
            </li>
            <li style="display: flex; gap: 0.5rem; align-items: flex-start;">
                <span style="color: #ffd600; font-weight: bold; font-family: var(--font-mono);">[BUDGET]</span>
                <span><strong>${cheapestPrice.car.Car_Name}</strong> (${cheapestPrice.car.Year}) provides the <strong>Lowest Acquisition Cost</strong>, requiring an initial outlay of just <strong>${cheapestPrice.car.Selling_Price.toFixed(2)} Lakhs</strong>.</span>
            </li>
        </ul>
        <p style="margin-top: 1rem; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem; font-style: italic; color: var(--text-muted);">
            🚀 <strong>Verdict Conclusion</strong>: If depreciation protection is your main goal, buy the <strong>${bestValue.car.Car_Name}</strong>. If you want a fresh engine, choose the <strong>${lowestKms.car.Car_Name}</strong>.
        </p>
    `;
    
    dom.conclusionText.innerHTML = conclusionHtml;
    dom.conclusionBox.classList.remove('hidden');
    
    // 3. Draw Multi-Line Chart (Chart.js)
    if (appState.forecastChart) {
        appState.forecastChart.destroy();
    }
    
    const labels = ["Present", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"];
    
    // Clean telemetry color list
    const chartColors = [
        '#d50000', // Rosso Red
        '#00e5ff', // Ice Cyan
        '#ffd600', // Rev Yellow
        '#00e676', // Emerald Green
        '#cfd8dc'  // Brushed Aluminum
    ];
    
    const datasets = scoredResults.map((r, i) => {
        const color = chartColors[i % chartColors.length];
        return {
            label: r.car.Car_Name + ` (${r.car.Year})`,
            data: [r.car.Selling_Price, r.yr1, r.forecast[1].estimated_value, r.yr3, r.forecast[3].estimated_value, r.yr5],
            borderColor: color,
            borderWidth: 2,
            backgroundColor: 'transparent',
            tension: 0.3,
            pointBackgroundColor: color,
            pointBorderColor: '#ffffff',
            pointHoverRadius: 7,
            pointRadius: 4
        };
    });
    
    const ctx = dom.chartCanvas.getContext('2d');
    appState.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#94a3b8',
                        font: {
                            family: 'Outfit',
                            size: 11
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Outfit'
                        }
                    },
                    min: 0
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'Outfit'
                        }
                    }
                }
            }
        }
    });
}

// Custom Valuation Form Handler
async function handleEstimate(e) {
    e.preventDefault();
    
    const reqBody = {
        Car_Name: dom.estCarName.value.trim(),
        Present_Price: parseFloat(dom.estPresentPrice.value),
        Kms_Driven: parseFloat(dom.estKms.value),
        Year: parseInt(dom.estYear.value),
        Fuel_Type: dom.estFuel.value,
        Seller_Type: dom.estSeller.value,
        Transmission: dom.estTransmission.value,
        Owner: parseInt(dom.estOwner.value)
    };
    
    try {
        const submitBtn = dom.estimatorForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<div class="spinner" style="width: 16px; height: 16px;"></div> <span>Calculating valuation...</span>`;
        
        const res = await fetch(`${API_BASE}/api/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(reqBody)
        });
        
        if (!res.ok) throw new Error("Estimator request failed");
        const data = await res.json();
        
        showEstimateResult(reqBody, data);
        
    } catch (err) {
        console.error("Estimator error:", err);
        alert("Valuation calculation failed. Check if API is running.");
    } finally {
        const submitBtn = dom.estimatorForm.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i data-lucide="sparkles"></i> <span>Estimate Resale Value</span>`;
        lucide.createIcons();
    }
}

// Show estimate results on DOM
function showEstimateResult(inputs, results) {
    dom.estimatorResultEmpty.classList.add('hidden');
    dom.estimatorResultContent.classList.remove('hidden');
    
    dom.resultCarTitle.textContent = `${inputs.Car_Name} (${inputs.Year})`;
    dom.resultSellingPrice.textContent = results.predicted_selling_price.toFixed(2);
    dom.resultPresentPrice.textContent = `${inputs.Present_Price.toFixed(2)} Lakhs`;
    dom.resultDepreciation.textContent = `${results.predicted_depreciation.toFixed(2)} Lakhs`;
    
    const retainedPct = (results.predicted_selling_price / inputs.Present_Price * 100).toFixed(1);
    dom.resultRetainedPct.textContent = `${retainedPct}%`;
    dom.resultAge.textContent = `${results.car_age} ${results.car_age === 1 ? 'Year' : 'Years'}`;
    
    // Dynamic color class for retained percentage
    dom.resultRetainedPct.className = "bd-val";
    if (retainedPct >= 70) {
        dom.resultRetainedPct.classList.add("success");
    } else if (retainedPct >= 40) {
        dom.resultRetainedPct.classList.add("warning");
    } else {
        dom.resultRetainedPct.classList.add("danger");
    }
}

// Model Retraining Handler
async function handleRetrain() {
    try {
        dom.btnRetrain.disabled = true;
        dom.btnRetrain.innerHTML = `<div class="spinner" style="width: 16px; height: 16px;"></div> <span>Retraining...</span>`;
        
        appendLog("Connecting to API server and fetching dataset...");
        appendLog("Re-engineering features: Age calculation relative to 2025 and Depreciation values...");
        appendLog("Fitting Scikit-Learn Linear Regression Pipeline...");
        
        const res = await fetch(`${API_BASE}/api/retrain`, { method: "POST" });
        if (!res.ok) throw new Error("Retrain endpoint failed");
        const data = await res.json();
        
        appendLog(`[Success] Pipeline refitted successfully!`);
        appendLog(`New R2 Score: ${data.metrics.r2_score.toFixed(4)}`);
        appendLog(`New MAE: ${data.metrics.mae.toFixed(4)} Lakhs`);
        
        // Refresh values on UI
        loadModelInfo();
        loadStats();
        loadCars();
        
    } catch (err) {
        appendLog(`[Error] Model retraining failed: ${err.message}`);
        console.error("Retrain error:", err);
    } finally {
        dom.btnRetrain.disabled = false;
        dom.btnRetrain.innerHTML = `<i data-lucide="refresh-cw"></i> <span>Retrain Model Now</span>`;
        lucide.createIcons();
    }
}

// Append log to console emulator
function appendLog(msg) {
    const timestamp = new Date().toLocaleTimeString();
    const logLine = `\n[${timestamp}] ${msg}`;
    dom.retrainConsole.textContent += logLine;
    dom.retrainConsole.scrollTop = dom.retrainConsole.scrollHeight;
}

// Helper: Animate number counter
function animateValue(obj, start, end, duration, suffix = "", isInt = false) {
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = progress * (end - start) + start;
        
        if (isInt) {
            obj.innerHTML = Math.floor(current).toLocaleString() + suffix;
        } else {
            obj.innerHTML = current.toFixed(2) + suffix;
        }
        
        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            if (isInt) {
                obj.innerHTML = end.toLocaleString() + suffix;
            } else {
                obj.innerHTML = end.toFixed(2) + suffix;
            }
        }
    };
    window.requestAnimationFrame(step);
}
