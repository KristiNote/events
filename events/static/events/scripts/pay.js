fetch(PAYMENTS_KEY_URL)
  .then((result) => { return result.json(); })
  .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);
    const eventListElem = document.querySelector('.event-list');
    eventListElem.addEventListener("click", (event) => {
        if (event.target.hasAttribute("data-purchase")) {
            const btn = event.target;
            const url = btn.dataset.checkoutSessionUrl;

            fetch(url)
              .then((result) => {
                  if (result.status >= 200 && result.status <= 299) {
                    return Promise.resolve(result.json());
                  } else {
                    return Promise.reject(result.json());
                  }
               })
              .then((data) => {
                console.log(data);
                // Redirect to Stripe Checkout
                return stripe.redirectToCheckout({sessionId: data.sessionId})
              })
              .then((res) => {
                console.log(res);
              }).catch(err => {
                console.error("THERE WAS AN ERROR!");
              });
        }

    });
  });
