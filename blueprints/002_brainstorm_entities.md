# Domain Model Brainstorming Prompts

## Core Entity Identification

1.  **Core Purpose:** What is the single most important problem this system solves? What is the primary entity or concept at the heart of that solution? (e.g., "A `Booking` in a reservation system," "A `Shipment` in a logistics system.")
2.  **Key Actors:** Who are the primary actors interacting with the system (users, other systems)? What are their goals? What nouns do they use when describing their work?
3.  **The "Thing":** If you had to describe the system's main "thing," what would it be? What information is essential to define it? (e.g., A `Product` must have a name, SKU, and price).
4.  **Lifecycle Events:** What are the major states or stages this "thing" goes through? (e.g., An `Order` goes from `Pending` -> `Processing` -> `Shipped` -> `Delivered`). These often reveal related entities or value objects.

## Bounded Context & Relationships

5.  **System Boundaries:** What is definitively *in* scope for this domain versus *out* of scope? Where does our model's responsibility end and another system's begin? (e.g., "We handle `Inventory`, but the `Shipping` service handles `Fulfillment`.")
6.  **Connecting the Dots:** How do the core entities relate to each other? Are they one-to-one, one-to-many, or many-to-many? (e.g., "A `Customer` can have many `Orders`," "An `Order` contains many `LineItems`.")
7.  **Ubiquitous Language:** List key terms used by domain experts. Are there any ambiguities or synonyms? Define them clearly. This list becomes the vocabulary for our model. (e.g., Is it a "User," "Customer," or "Client"? Let's agree on one.)

## Properties & Invariants

8.  **Essential Data:** For each entity, what information is absolutely required for it to be valid? What can never change? These are your invariants. (e.g., "An `Invoice` number, once assigned, can never be altered.")
9.  **Value Objects:** What descriptive attributes of an entity have no identity on their own but are important for defining the model? (e.g., `Address` (street, city, zip), `Money` (amount, currency)).
10. **Rules & Policies:** What are the business rules that govern the system? (e.g., "A `User` cannot be deleted if they have placed an `Order`," "A `Discount` can only be applied to non-sale items.")

## "What If" Scenarios

11. **Edge Cases:** Brainstorm potential edge cases and failure modes. What happens if a payment fails? What if a product is out of stock? How does the model handle these scenarios?
12. **Future-Proofing:** What is the most likely way this system will need to change or grow in the next year? How can we design the model to accommodate that change without a major rewrite? 