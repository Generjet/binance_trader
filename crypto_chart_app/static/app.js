const chartContainer = document.getElementById('chart-container');
const cryptoInput = document.getElementById('crypto');
const intervalInput = document.getElementById('interval');
const fetchButton = document.getElementById('fetch-button');

const margin = { top: 50, right: 50, bottom: 50, left: 50 };
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

const svg = d3.select("#chart-container")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

const x = d3.scaleBand().range([0, width]).padding(0.1);
const y = d3.scaleLinear().range([height, 0]);

let chartData = [];

function createChart(data, extremumPoints) {
    x.domain(data.map(d => d.time));
    y.domain([d3.min(data, d => d.low), d3.max(data, d => d.high)]);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d %H:%M")));

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

    if (extremumPoints) {
        svg.selectAll(".extremum")
            .data(extremumPoints)
            .enter()
            .append("circle")
            .attr("class", "extremum")
            .attr("cx", d => x(d.time) + x.bandwidth() / 2)
            .attr("cy", d => y(d.value))
            .attr("r", 5)
            .attr("fill", d => d.type === "max" ? "blue" : "orange");
    }
}

function updateChart(newData, extremumPoints, isDoji, signal) {
    if (newData) {
        chartData.push(newData);
        if (chartData.length > 100) {
            chartData.shift();
        }
    }

    svg.selectAll("*").remove();
    createChart(chartData, extremumPoints);

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
}

const socket = io('http://localhost:5000', {
    query: {
        symbol: cryptoInput.value.toUpperCase(),
        interval: intervalInput.value
    }
});

socket.on('update_data', function(data) {
    updateChart(data.data, data.extremum_points, data.is_doji, data.signal);
});

fetchButton.addEventListener('click', () => {
    const crypto = cryptoInput.value.toUpperCase();
    const interval = intervalInput.value;
    socket.io.opts.query = { symbol: crypto, interval: interval };
});
