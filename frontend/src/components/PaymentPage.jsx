import { useState } from "react";
import {
  Elements,
  PaymentElement,
  useElements,
  useStripe,
} from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { formatPrice } from "../api/products.js";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

function PaymentForm({ clientSecret, order, onBack }) {
  const stripe = useStripe();
  const elements = useElements();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [succeeded, setSucceeded] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);

    // Обязательно вызываем ДО confirmPayment().
    // Stripe требует сделать это сразу после нажатия Pay.
    const { error: submitError } = await elements.submit();

    if (submitError) {
      setError(submitError.message);
      setLoading(false);
      return;
    }

    const { error: confirmError } = await stripe.confirmPayment({
      elements,
      clientSecret,
      confirmParams: {
        return_url: window.location.origin,
      },
      redirect: "if_required",
    });

    if (confirmError) {
      setError(confirmError.message);
      setLoading(false);
      return;
    }

    setSucceeded(true);
    setLoading(false);
  };

  return (
    <div className="payment">
      <button
        type="button"
        className="payment__back"
        onClick={onBack}
        disabled={loading}
      >
        ← Назад к товарам
      </button>

      <div className="payment__panel">
        <h2 className="payment__title">Оплата</h2>

        <p className="payment__order">Заказ №{order.id}</p>
        <p className="payment__amount">
          {formatPrice(order.amount, order.currency)}
        </p>

        {succeeded ? (
          <p className="payment__success">
            Оплата прошла успешно
          </p>
        ) : (
          <form className="payment__form" onSubmit={handleSubmit}>
            <PaymentElement options={{ layout: "tabs" }} />

            {error && (
              <p className="payment__error">
                Ошибка: {error}
              </p>
            )}

            <button
              type="submit"
              className="payment__button"
              disabled={!stripe || loading}
            >
              {loading ? "Оплата…" : "Оплатить"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default function PaymentPage({
  clientSecret,
  order,
  onBack,
}) {
  return (
    <Elements
      stripe={stripePromise}
      options={{
        clientSecret,
        appearance: {
          theme: "stripe",
        },
      }}
    >
      <PaymentForm
        clientSecret={clientSecret}
        order={order}
        onBack={onBack}
      />
    </Elements>
  );
}