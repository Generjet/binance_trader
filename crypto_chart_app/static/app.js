const chartContainer = document.getElementById('chart-container');
const cryptoInput = document.getElementById('crypto');
const intervalInput = document.getElementById('interval');
const fetchButton = document.getElementById('fetch-button');
const dataTable = document.getElementById('data-table').getElementsByTagName('tbody')[0];

const margin = { top: 20, right: 50, bottom: 20, left: 50 };
let width = window.innerWidth - margin.left - margin.right - 40; // Adjust width dynamically
const height = 400 - margin.top - margin.bottom;
const indicatorHeight = 100; // Height for each indicator chart

// Main chart SVG
const svg = d3.select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom + 4 * indicatorHeight) // Increased height for indicators
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// RSI chart SVG
const svgRSI = d3.select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", indicatorHeight + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// MACD chart SVG
const svgMACD = d3.select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", indicatorHeight + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

const x = d3.scaleBand().range([0, width]).padding(0.1);
const y = d3.scaleLinear().range([height, 0]);
const yRSI = d3.scaleLinear().range([indicatorHeight, 0]);
const yMACD = d3.scaleLinear().range([indicatorHeight, 0]);

let chartData = [];

function createChart(data) {
    if (!data || data.length === 0) return;

    x.domain(data.map(d => d.time));
    y.domain([d3.min(data, d => d.low), d3.max(data, d => d.high)]);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickFormat(d3.utcFormat("%Y-%m-%d %H:%M")));

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.selectAll(".candlestick")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "candlestick")
        .attr("x", d => x(d.time))
        .attr("y", d => y(Math.max(d.open, d.close)))
        .attr("height", d => Math.abs(y(d.open) - y(d.close)))
        .attr("width", x.bandwidth())
        .attr("fill", d => d.open > d.close ? "red" : "green");

    svg.selectAll(".line")
        .data(data)
        .enter()
        .append("line")
        .attr("class", "line")
        .attr("x1", d => x(d.time) + x.bandwidth() / 2)
        .attr("y1", d => y(d.high))
        .attr("x2", d => x(d.time) + x.bandwidth() / 2)
        .attr("y2", d => y(d.low))
        .attr("stroke", "black");
}

function drawRSIChart(data) {
    if (!data || data.length === 0) return;

    yRSI.domain([0, 100]);

    svgRSI.append("g")
        .attr("transform", "translate(0," + indicatorHeight + ")")
        .call(d3.axisBottom(x).tickFormat(d3.utcFormat("%Y-%m-%d %H:%M")));

    svgRSI.append("g")
        .call(d3.axisLeft(yRSI));

    svgRSI.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "purple")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(d => x(d.time) + x.bandwidth() / 2)
            .y(d => yRSI(d.rsi))
        );
}

function drawMACDChart(data) {
    if (!data || data.length === 0) return;

    yMACD.domain([d3.min(data, d => d.macd), d3.max(data, d => d.macd)]);

    svgMACD.append("g")
        .attr("transform", "translate(0," + indicatorHeight + ")")
        .call(d3.axisBottom(x).tickFormat(d3.utcFormat("%Y-%m-%d %H:%M")));

    svgMACD.append("g")
        .call(d3.axisLeft(yMACD));

    svgMACD.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
            .x(d => x(d.time) + x.bandwidth() / 2)
            .y(d => yMACD(d.macd))
        );

    // Volume bars
    const maxVolume = d3.max(data, d => d.volume);
    const yVolume = d3.scaleLinear()
        .range([indicatorHeight, indicatorHeight * 0.6]) // Using 40% of the height for volume
        .domain([0, maxVolume]);

    svgMACD.selectAll(".volume-bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "volume-bar")
        .attr("x", d => x(d.time))
        .attr("y", d => yVolume(d.volume))
        .attr("height", d => indicatorHeight - yVolume(d.volume))
        .attr("width", x.bandwidth())
        .attr("fill", "gray");
}

function createTable(data) {
    if (!data || data.length === 0) return;

    // Create table headers
    let headers = Object.keys(data[0]);
    let headerRow = dataTable.insertRow();
    headers.forEach(header => {
        let th = document.createElement("th");
        th.textContent = header;
        headerRow.appendChild(th);
    });
}

function updateTable(newData) {
    if (!newData) return;

    let row = dataTable.insertRow();
    Object.values(newData).forEach(value => {
        let cell = row.insertCell();
        cell.textContent = value;
    });
}

function updateChart(newData, extremumPoints, isDoji, signal, support, resistance) {
    if (newData) {
        chartData.push(newData);
        if (chartData.length > 100) {
            chartData.shift();
        }
    }

    svg.selectAll("*").remove();
    svgRSI.selectAll("*").remove();
    svgMACD.selectAll("*").remove();

    createChart(chartData, extremumPoints);
    drawRSIChart(chartData);
    drawMACDChart(chartData);

    // Draw support and resistance lines
    console.log("Support:", support); // Debugging log
    console.log("Resistance:", resistance); // Debugging log
    console.log("y scale:", y.domain()); // Debugging log
    if (support && y) {
        svg.append("line")
            .attr("class", "support")
            .attr("x1", 0)
            .attr("y1", y(support))
            .attr("x2", width)
            .attr("y2", y(support))
            .attr("stroke", "green")
            .attr("stroke-width", 2);
    }

    if (resistance && y) {
        svg.append("line")
            .attr("class", "resistance")
            .attr("x1", 0)
            .attr("y1", y(resistance))
            .attr("x2", width)
            .attr("y2", y(resistance))
            .attr("stroke", "red")
            .attr("stroke-width", 2);
    }

    if (isDoji) {
        svg.append("polygon")
            .attr("points", `${x(newData.time) + x.bandwidth() / 2},${y(newData.high) - 15} ${x(newData.time) + x.bandwidth() / 2 - 5},${y(newData.high) - 5} ${x(newData.time) + x.bandwidth() / 2 + 5},${y(newData.high) - 5}`)
            .attr("fill", "purple");
    }

    if (signal) {
        let signalText = signal.toUpperCase();
        let signalColor = signal === "buy" ? "green" : "red";
        let signalY = signal === "buy" ? y(newData.low) + 20 : y(newData.high) - 20;

        svg.append("text")
            .attr("x", x(newData.time) + x.bandwidth() / 2)
            .attr("y", signalY)
            .attr("text-anchor", "middle")
            .attr("fill", signalColor)
            .text(signalText);
    }

    updateTable(newData);
}

const socket = io('http://localhost:5000', {
    query: {
        symbol: cryptoInput.value.toUpperCase(),
        interval: intervalInput.value
    }
});

socket.on('update_data', function(data) {
    console.log("Received data:", data); // Debugging log
    updateChart(data.data, data.extremum_points, data.is_doji, data.signal, data.support, data.resistance);
});

fetchButton.addEventListener('click', () => {
    const crypto = cryptoInput.value.toUpperCase();
    const interval = intervalInput.value;
    socket.io.opts.query = { symbol: crypto, interval: interval };
});

// Initialize the table
createTable([
    {
        time: '',
        open: '',
        high: '',
        low: '',
        close: '',
        volume: '',
        macd: '',
        rsi: '',
        '%K': '',
        '%D': '',
        ema: '',
        support: '',
        resistance: '',
        is_doji: '',
        signal: ''
    }
]);

// Resize chart on window resize
window.addEventListener('resize', () => {
    width = window.innerWidth - margin.left - margin.right - 40; // Update width
    x.range([0, width]); // Update x scale range
    svg.attr("width", width + margin.left + margin.right);
    svgRSI.attr("width", width + margin.left + margin.right);
    svgMACD.attr("width", width + margin.left + margin.right);
    svg.selectAll("*").remove();
    svgRSI.selectAll("*").remove();
    svgMACD.selectAll("*").remove();
    createChart(chartData);
    drawRSIChart(chartData);
    drawMACDChart(chartData);
});
