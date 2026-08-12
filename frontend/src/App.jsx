import { useEffect, useState } from "react";
import { getProducts, CURRENCY_LABELS } from "./api/products.js";
import ProductCard from "./components/ProductCard.jsx";

const CURRENCIES = ["usd", "rub", "eur"];

export default function App() {
  const [currency, setCurrency] = useState("usd");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);
    getProducts(currency)
      .then((result) => {
        if (!cancelled) setProducts(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [currency]);

  return (
    <div className="app">
      <header className="app__header">
        <h1>Товары</h1>
        <div className="app__currencies">
          {CURRENCIES.map((cur) => (
            <button
              key={cur}
              type="button"
              className="app__currency"
              data-active={currency === cur}
              onClick={() => setCurrency(cur)}
            >
              {CURRENCY_LABELS[cur]}
            </button>
          ))}
        </div>
      </header>

      {loading && <p className="app__status">Загрузка…</p>}
      {error && <p className="app__status app__status--error">Ошибка: {error}</p>}

      {!loading && !error && products.length === 0 && (
        <p className="app__status">Нет товаров</p>
      )}

      {!loading && !error && products.length > 0 && (
        <div className="app__grid">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}