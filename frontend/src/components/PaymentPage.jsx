import { useState } from "react";
import {
  Elements,
  PaymentElement,
  useElements,
  useStripe,
} from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

function PaymentForm({ clientSecret, product, onBack }) {
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

    const { error: submitError } = await stripe.confirmPayment({
      elements,
      clientSecret,
      confirmParams: {
        return_url: window.location.origin,
      },
      redirect: "if_required",
    });

    if (submitError) {
      setError(submitError.message);
      setLoading(false);
      return;
    }

    setSucceeded(true);
    setLoading(false);
  };

  return (
    <div className="payment">
      <button type="button" className="payment__back" onClick={onBack}>
        ← Назад к товарам
      </button>
      <div className="payment__panel">
        <h2 className="payment__title">Оплата</h2>
        <p className="payment__product">
          {product.name}
          {product.priceLabel ? ` — ${product.priceLabel}` : ""}
        </p>

        {succeeded ? (
          <p className="payment__success">Оплата прошла успешно</p>
        ) : (
          <form className="payment__form" onSubmit={handleSubmit}>
            <PaymentElement options={{ layout: "tabs" }} />
            {error && <p className="payment__error">Ошибка: {error}</p>}
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

export default function PaymentPage({ clientSecret, product, onBack }) {
  return (
    <Elements
      stripe={stripePromise}
      options={{ clientSecret, appearance: { theme: "stripe" } }}
    >
      <PaymentForm
        clientSecret={clientSecret}
        product={product}
        onBack={onBack}
      />
    </Elements>
  );
}
