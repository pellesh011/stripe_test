import { useEffect, useState } from "react";
import { getOrders } from "../api/orders.js";
import { formatPrice } from "../api/products.js";

const ORDER_STATUS_LABELS = {
  created: "Создан",
  pending_payment: "Ожидает оплаты",
  paid: "Оплачен",
  processing: "Обрабатывается",
  shipped: "Отправлен",
  completed: "Выполнен",
  cancelled: "Отменён",
  refunded: "Возвращён",
};

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getOrders()
      .then((result) => {
        if (!cancelled) setOrders(result);
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
  }, []);

  if (loading) {
    return <p className="app__status">Загрузка…</p>;
  }

  if (error) {
    return <p className="app__status app__status--error">Ошибка: {error}</p>;
  }

  if (orders.length === 0) {
    return <p className="app__status">Заказов пока нет</p>;
  }

  return (
    <div className="page">
      <h2 className="page__title">Заказы</h2>
      <div className="orders">
        {orders.map((order) => (
          <div className="order" key={order.id}>
            <div className="order__header">
              <div className="order__title">
                <span className="order__number">Заказ №{order.id}</span>
                <span className="order__date">{formatDate(order.created_at)}</span>
              </div>
              <span
                className={`order__status order__status--${order.status}`}
              >
                {ORDER_STATUS_LABELS[order.status] || order.status}
              </span>
            </div>
            <ul className="order__items">
              {order.items.map((item, index) => (
                <li className="order__item" key={`${order.id}-${index}`}>
                  <span className="order__item-name">{item.product_name}</span>
                  <span className="order__item-price">
                    {formatPrice(item.price, item.currency)}
                  </span>
                </li>
              ))}
            </ul>
            <div className="order__footer">
              <span>Итого:</span>
              <span className="order__total">
                {formatPrice(order.total, order.currency)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}