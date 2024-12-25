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

function createChart(data) {
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
}

async function updateChart() {
    const crypto = cryptoInput.value.toUpperCase();
    const interval = intervalInput.value;
    const apiUrl = `http://localhost:5000/chart?symbol=${crypto}&interval=${interval}`;

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        svg.selectAll("*").remove();
        createChart(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

fetchButton.addEventListener('click', updateChart);

setInterval(updateChart, 3000);

updateChart();
