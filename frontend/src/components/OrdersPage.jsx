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

function formatDiscountLabel(order) {
  if (!order.discount) return "—";
  const { name, type, value } = order.discount;
  if (type === "percentage") {
    return `${name} · ${value}%`;
  }
  return `${name} · −${formatPrice(value, order.currency)}`;
}

function formatTaxLabel(order) {
  if (!order.tax) return "—";
  return `${order.tax.name} · ${order.tax.rate}%`;
}

const PER_PAGE = 10;

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

export default function OrdersPage({ onPay, onBackToProducts }) {
  const [orders, setOrders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    getOrders({
      limit: PER_PAGE,
      offset: (page - 1) * PER_PAGE,
    })
      .then((result) => {
        if (!cancelled) {
          setOrders(result.orders);
          setTotal(result.total);
        }
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
  }, [page]);

  if (loading) {
    return <p className="app__status">Загрузка…</p>;
  }

  if (error) {
    return <p className="app__status app__status--error">Ошибка: {error}</p>;
  }

  const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));

  return (
    <div className="page">
      <h2 className="page__title">Заказы</h2>
      {total === 0 ? (
        <p className="app__status">Заказов пока нет</p>
      ) : (
        <>
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
                  <div className="order__item-prices">
                    <span className="order__item-original">
                      {formatPrice(item.product_price.price, item.product_price.currency)}
                    </span>
                    <span className="order__item-price">
                      {formatPrice(item.price, item.currency)}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
            <div className="order__footer">
              <div className="order__footer-row">
                <span>Скидка</span>
                <span>{formatDiscountLabel(order)}</span>
              </div>
              <div className="order__footer-row">
                <span>Налог</span>
                <span>{formatTaxLabel(order)}</span>
              </div>
              <div className="order__footer-row">
                <span>Сумма</span>
                <span>{formatPrice(order.subtotal, order.currency)}</span>
              </div>
              <div className="order__footer-row">
                <span>Сумма с discount</span>
                <span>
                  {formatPrice(
                    (Number(order.subtotal) - Number(order.discount_amount)).toFixed(2),
                    order.currency
                  )}
                </span>
              </div>
              <div className="order__footer-row">
                <span>Сумма с tax</span>
                <span>
                  {formatPrice(
                    (Number(order.subtotal) - Number(order.discount_amount) + Number(order.tax_amount)).toFixed(2),
                    order.currency
                  )}
                </span>
              </div>
              <div className="order__footer-row order__footer-row--total">
                <span>Итого</span>
                <span className="order__total">
                  {formatPrice(order.total, order.currency)}
                </span>
              </div>
            </div>
            {(order.status === "created" || order.status === "pending_payment") &&
              order.payment_intent && (
                <button
                  type="button"
                  className="order__pay"
                  onClick={() => onPay(order)}
                >
                  Оплатить
                </button>
              )}
          </div>
        ))}
      </div>
          <div className="pagination">
            <button
              type="button"
              className="button"
              disabled={page <= 1}
              onClick={() => setPage((current) => current - 1)}
            >
              ← Назад
            </button>
            <span className="pagination__info">
              Страница {page} из {totalPages}
            </span>
            <button
              type="button"
              className="button"
              disabled={page >= totalPages}
              onClick={() => setPage((current) => current + 1)}
            >
              Вперёд →
            </button>
          </div>
        </>
      )}
      <div className="page__actions">
        <button type="button" className="button" onClick={onBackToProducts}>
          К товарам
        </button>
      </div>
    </div>
  );
}