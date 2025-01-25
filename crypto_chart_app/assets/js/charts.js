document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    let currentPage = 1;
    const rowsPerPage = 30;

    const toggleButton = document.getElementById('toggleButton');
    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('default-mode');
        updateChart(JSON.parse(document.getElementById('chart').dataset.chartData));
    });

    socket.on('new_data', (data) => {
        document.getElementById('latest-open').innerText = data.open;
        document.getElementById('latest-high').innerText = data.high;
        document.getElementById('latest-low').innerText = data.low;
        document.getElementById('latest-close').innerText = data.close;

        // Update chart
        const chartDiv = document.getElementById('chart');
        const chartData = JSON.parse(chartDiv.dataset.chartData);
        chartData.unshift(data);
        chartDiv.dataset.chartData = JSON.stringify(chartData);
        updateChart(chartData);

        // Update table
        const tableDiv = document.getElementById('table');
        const tableData = JSON.parse(tableDiv.dataset.tableData);
        tableData.unshift(data);
        tableDiv.dataset.tableData = JSON.stringify(tableData);
        updateTable(tableData, currentPage, rowsPerPage);
    });

    function updateChart(data) {
        const isDarkMode = document.body.classList.contains('dark-mode');
        const template = isDarkMode ? 'plotly_dark' : 'plotly_white';
        const fontColor = isDarkMode ? 'white' : 'black';
        const plotBgColor = isDarkMode ? 'black' : 'white';
        const paperBgColor = isDarkMode ? 'black' : 'white';

        const candlestick = {
            x: data.map(d => d.time),
            open: data.map(d => d.open),
            high: data.map(d => d.high),
            low: data.map(d => d.low),
            close: data.map(d => d.close),
            type: 'candlestick',
            increasing: { line: { color: 'green' } },
            decreasing: { line: { color: 'red' } }
        };

        const ema = {
            x: data.map(d => d.time),
            y: data.map(d => d.ema),
            type: 'scatter',
            mode: 'lines',
            name: 'EMA',
            line: { color: 'blue' }
        };

        const resistance = {
            x: data.map(d => d.time),
            y: data.map(d => d.resistance),
            type: 'scatter',
            mode: 'lines',
            name: 'Resistance',
            line: { color: 'orange', dash: 'dash' }
        };

        const support = {
            x: data.map(d => d.time),
            y: data.map(d => d.support),
            type: 'scatter',
            mode: 'lines',
            name: 'Support',
            line: { color: 'red', dash: 'dash' }
        };

        const volume = {
            x: data.map(d => d.time),
            y: data.map(d => d.volume),
            type: 'bar',
            name: 'Volume',
            marker: {
                color: data.map(d => d.close > d.open ? 'green' : 'red')
            }
        };

        const macd = {
            x: data.map(d => d.time),
            y: data.map(d => d.macd),
            type: 'scatter',
            mode: 'lines',
            name: 'MACD',
            line: { color: 'cyan' }
        };

        const rsi = {
            x: data.map(d => d.time),
            y: data.map(d => d.rsi),
            type: 'scatter',
            mode: 'lines',
            name: 'RSI',
            line: { color: 'magenta' }
        };

        const stochasticK = {
            x: data.map(d => d.time),
            y: data.map(d => d.stochastic_K),
            type: 'scatter',
            mode: 'lines',
            name: 'Stochastic %K',
            line: { color: 'yellow' }
        };

        const stochasticD = {
            x: data.map(d => d.time),
            y: data.map(d => d.stochastic_D),
            type: 'scatter',
            mode: 'lines',
            name: 'Stochastic %D',
            line: { color: 'red' }
        };

        const layoutCandlestick = {
            template: template,
            xaxis: { rangeslider: { visible: false } },
            title: 'Crypto Price Data',
            yaxis: { title: 'Price', color: fontColor },
            xaxis: { title: 'Time', color: fontColor },
            plot_bgcolor: plotBgColor,
            paper_bgcolor: paperBgColor,
            font: { color: fontColor },
            legend: { font: { color: fontColor } }
        };

        const layoutVolume = {
            template: template,
            title: 'Volume',
            yaxis: { title: 'Volume', color: fontColor },
            xaxis: { title: 'Time', color: fontColor },
            plot_bgcolor: plotBgColor,
            paper_bgcolor: paperBgColor,
            font: { color: fontColor },
            legend: { font: { color: fontColor } }
        };

        const layoutMACD = {
            template: template,
            title: 'MACD',
            yaxis: { title: 'MACD', color: fontColor },
            xaxis: { title: 'Time', color: fontColor },
            shapes: [
                { type: 'line', x0: 0, x1: 1, y0: 20, y1: 20, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } },
                { type: 'line', x0: 0, x1: 1, y0: 80, y1: 80, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } },
                { type: 'line', x0: 0, x1: 1, y0: 0, y1: 0, xref: 'paper', yref: 'y', line: { color: 'white', dash: 'dash' } }
            ],
            plot_bgcolor: plotBgColor,
            paper_bgcolor: paperBgColor,
            font: { color: fontColor },
            legend: { font: { color: fontColor } }
        };

        const layoutRSI = {
            template: template,
            title: 'RSI',
            yaxis: { title: 'RSI', color: fontColor },
            xaxis: { title: 'Time', color: fontColor },
            shapes: [
                { type: 'line', x0: 0, x1: 1, y0: 20, y1: 20, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } },
                { type: 'line', x0: 0, x1: 1, y0: 80, y1: 80, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } }
            ],
            plot_bgcolor: plotBgColor,
            paper_bgcolor: paperBgColor,
            font: { color: fontColor },
            legend: { font: { color: fontColor } }
        };

        const layoutStochastic = {
            template: template,
            title: 'Stochastic',
            yaxis: { title: 'Stochastic', color: fontColor },
            xaxis: { title: 'Time', color: fontColor },
            shapes: [
                { type: 'line', x0: 0, x1: 1, y0: 20, y1: 20, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } },
                { type: 'line', x0: 0, x1: 1, y0: 80, y1: 80, xref: 'paper', yref: 'y', line: { color: 'red', dash: 'dash' } }
            ],
            plot_bgcolor: plotBgColor,
            paper_bgcolor: paperBgColor,
            font: { color: fontColor },
            legend: { font: { color: fontColor } }
        };

        Plotly.newPlot('chart', [candlestick, ema, resistance, support], layoutCandlestick);
        Plotly.newPlot('volume-chart', [volume], layoutVolume);
        Plotly.newPlot('macd-chart', [macd], layoutMACD);
        Plotly.newPlot('rsi-chart', [rsi], layoutRSI);
        Plotly.newPlot('stochastic-chart', [stochasticK, stochasticD], layoutStochastic);
    }

    function updateTable(data, page, rowsPerPage) {
        const tableDiv = document.getElementById('table');
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        const paginatedData = data.slice(start, end);

        let tableHtml = '<table class="data"><thead><tr>';
        tableHtml += '<th>Time</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>';
        tableHtml += '</tr></thead><tbody>';

        paginatedData.forEach(row => {
            tableHtml += `<tr>
                <td>${row.time}</td>
                <td>${row.open}</td>
                <td>${row.high}</td>
                <td>${row.low}</td>
                <td>${row.close}</td>
                <td>${row.volume}</td>
            </tr>`;
        });

        tableHtml += '</tbody></table>';
        tableDiv.innerHTML = tableHtml;
    }

    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            const tableData = JSON.parse(document.getElementById('table').dataset.tableData);
            updateTable(tableData, currentPage, rowsPerPage);
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const tableData = JSON.parse(document.getElementById('table').dataset.tableData);
        if (currentPage * rowsPerPage < tableData.length) {
            currentPage++;
            updateTable(tableData, currentPage, rowsPerPage);
        }
    });

    // Initial chart and table setup
    const initialChartData = JSON.parse(document.getElementById('chart').dataset.chartData);
    updateChart(initialChartData);
    const initialTableData = JSON.parse(document.getElementById('table').dataset.tableData);
    updateTable(initialTableData, currentPage, rowsPerPage);
});