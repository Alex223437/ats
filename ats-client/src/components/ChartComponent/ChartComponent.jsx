import React, { useEffect, useState } from 'react';
import { fetchStockData } from '../../services/stockService';
import { fetchStrategies } from '../../services/strategyService';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import './ChartComponent.scss';

const ChartComponent = ({ ticker }) => {
  const [data, setData] = useState([]);
  const [yDomain, setYDomain] = useState([0, 100]);
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);

  // Загружаем стратегии
  useEffect(() => {
    const loadStrategies = async () => {
      const strategiesData = await fetchStrategies();
      setStrategies(strategiesData);
    };
    loadStrategies();
  }, []);

  // Загружаем данные по выбранной стратегии
  useEffect(() => {
    const loadData = async () => {
      if (!ticker) return;

      let result = []; // <=== Инициализируем переменную перед использованием

      try {
        if (selectedStrategy === 'AI Prediction') {
          result = await fetchStockData(ticker, 'ai'); // AI стратегия
        } else {
          result = await fetchStockData(ticker, selectedStrategy?.id || null); // Обычная стратегия
        }
        setData(result);

        // Рассчитываем границы оси Y
        if (result.length > 0) {
          const prices = result.map((d) => d.Close);
          let minPrice = Math.min(...prices);
          let maxPrice = Math.max(...prices);
          let margin = (maxPrice - minPrice) * 0.1;
          setYDomain([minPrice - margin, maxPrice + margin]);
        }
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      }
    };

    loadData();
  }, [ticker, selectedStrategy]); // обновляем при изменении тикера или стратегии

  // Кастомное отображение точек сигналов
  const customDot = (props) => {
    const { cx, cy, payload, index } = props;
    if (payload.Buy_Signal) {
      return (
        <svg x={cx - 7} y={cy - 7} width={14} height={14} viewBox="0 0 32 32" key={`buy-${index}`}>
          <polygon points="16,0 32,32 0,32" fill="green" />
        </svg>
      );
    }
    if (payload.Sell_Signal) {
      return (
        <svg x={cx - 7} y={cy - 7} width={14} height={14} viewBox="0 0 32 32" key={`sell-${index}`}>
          <polygon points="0,0 32,0 16,32" fill="red" />
        </svg>
      );
    }
    return null;
  };

  return (
    <div className="chart__wrapper">
      <h2 className="chart__subtitle">Graph of {ticker} stock</h2>
      {/* Дропдаун для выбора стратегии */}
      <div className="strategy-selector">
        <label>Select Strategy:</label>
        <select
          value={
            selectedStrategy?.id || (selectedStrategy === 'AI Prediction' ? 'AI Prediction' : '')
          }
          onChange={(e) => {
            if (e.target.value === 'AI Prediction') {
              setSelectedStrategy('AI Prediction');
            } else {
              const strategy = strategies.find((s) => s.id === Number(e.target.value));
              setSelectedStrategy(strategy || null);
            }
          }}
        >
          <option value="">Default Strategy</option>
          <option value="AI Prediction">AI Prediction</option>
          {strategies.map((strategy) => (
            <option key={strategy.id} value={strategy.id}>
              {strategy.title}
            </option>
          ))}
        </select>
      </div>

      <ResponsiveContainer width="100%" height="90%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="5 5" stroke="#e2e8f0" />
          <XAxis dataKey="Date" tick={{ fontSize: 12 }} tickMargin={10} />
          {/* Перемещаем ось Y вправо и задаём динамический диапазон */}
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            tickMargin={10}
            domain={yDomain}
            tickFormatter={(value) => value.toFixed(2)}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#f1f5f9', borderRadius: '10px', color: '#1f2937' }}
          />
          <Legend wrapperStyle={{ fontSize: 14 }} />

          {/* Линия цены с точками и сигналами */}
          <Line
            type="monotone"
            dataKey="Close"
            stroke="#4f46e5"
            strokeWidth={3}
            dot={customDot}
            name="Closing Price"
            yAxisId="right"
          />

          {/* 50-дневная SMA */}
          <Line
            type="monotone"
            dataKey="SMA_Short"
            stroke="#22c55e"
            strokeWidth={3}
            dot={false}
            name="SMA 10"
            yAxisId="right"
          />

          {/* 200-дневная SMA */}
          <Line
            type="monotone"
            dataKey="SMA_Long"
            stroke="#f97316"
            strokeWidth={3}
            dot={false}
            name="SMA 50"
            yAxisId="right"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChartComponent;
