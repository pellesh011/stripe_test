import { useCallback, useEffect, useState } from "react";
import { buyInOneClick, getProducts } from "./api/products.js";
import { addToCart, checkoutCart, getActiveCart } from "./api/cart.js";
import ProductCard from "./components/ProductCard.jsx";
import BuyInOneClickModal from "./components/BuyInOneClickModal.jsx";
import PaymentPage from "./components/PaymentPage.jsx";
import Header from "./components/Header.jsx";
import CartPage from "./components/CartPage.jsx";
import OrdersPage from "./components/OrdersPage.jsx";

export default function App() {
  const [view, setView] = useState("products");
  const [currency, setCurrency] = useState("usd");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [buyProduct, setBuyProduct] = useState(null);
  const [payment, setPayment] = useState(null);
  const [cart, setCart] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getActiveCart()
      .then((result) => {
        if (!cancelled) setCart(result);
      })
      .catch(() => {
        if (!cancelled) setCart(null);
      });

    return () => {
      cancelled = true;
    };
  }, []);

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

  const handleBuyOneClick = useCallback(
    async (productId, cur, discount) => {
      const price = buyProduct?.price ?? null;
      const result = await buyInOneClick(productId, price?.id, cur, discount);
      if (!result.client_secret) {
        throw new Error("Сервер не вернул client_secret");
      }
      setBuyProduct(null);
      setPayment({
        clientSecret: result.client_secret,
        order: {
          id: result.order_id,
          amount: result.amount,
          currency: result.currency,
        },
      });
    },
    [buyProduct]
  );

  const handleCartCheckout = useCallback(
    async (cartId, cur, discount) => {
      const result = await checkoutCart(cartId, cur, discount);
      if (!result.client_secret) {
        throw new Error("Сервер не вернул client_secret");
      }
      setCart(null);
      setPayment({
        clientSecret: result.client_secret,
        order: {
          id: result.order_id,
          amount: result.amount,
          currency: result.currency,
        },
      });
    },
    []
  );

  const handleAddToCart = useCallback(
    async (product, price) => {
      let cartId = cart?.id ?? null;
      if (!cartId) {
        const fresh = await getActiveCart();
        if (!fresh) {
          throw new Error("Не удалось получить корзину");
        }
        setCart(fresh);
        cartId = fresh.id;
      }

      const doAdd = async (id) => {
        const updated = await addToCart(product.id, price?.id, id);
        setCart(updated);
      };

      try {
        await doAdd(cartId);
      } catch (err) {
        if (err?.status === 400 && /not active/i.test(err.message)) {
          const fresh = await getActiveCart();
          if (!fresh) {
            throw err;
          }
          setCart(fresh);
          await doAdd(fresh.id);
          return;
        }
        throw err;
      }
    },
    [cart]
  );

  if (payment) {
    return (
      <PaymentPage
        clientSecret={payment.clientSecret}
        order={payment.order}
        onBack={() => setPayment(null)}
      />
    );
  }

  return (
    <div className="app">
      <Header
        view={view}
        onNavigate={setView}
        currency={currency}
        onCurrencyChange={setCurrency}
        cartItemCount={cart?.items?.length ?? 0}
      />

      {view === "products" && (
        <>
          {loading && <p className="app__status">Загрузка…</p>}
          {error && <p className="app__status app__status--error">Ошибка: {error}</p>}

          {!loading && !error && products.length === 0 && (
            <p className="app__status">Нет товаров</p>
          )}

          {!loading && !error && products.length > 0 && (
            <div className="app__grid">
              {products.map((product) => (
                <ProductCard
                  key={product.id}
                  product={product}
                  onBuyOneClick={(p, price) => setBuyProduct({ product: p, price })}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          )}

          {buyProduct && (
            <BuyInOneClickModal
              product={buyProduct.product}
              price={buyProduct.price}
              onClose={() => setBuyProduct(null)}
              onSubmit={handleBuyOneClick}
            />
          )}
        </>
      )}

      {view === "cart" && (
        <CartPage
          onBackToProducts={() => setView("products")}
          onCheckout={handleCartCheckout}
        />
      )}

      {view === "orders" && <OrdersPage />}
    </div>
  );
}
