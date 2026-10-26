# UX issues still open before production

Updated 27 October 2026. The current user-test build is `dist/user-test-site/`; the FigCraft file is a separate click-through.

| Priority | Issue | Next check |
| --- | --- | --- |
| High | FigCraft uses static example records. A reservation created for one customer can lead to a bill screen with another example customer; form controls do not change data. | Use the web prototype for task tests. Align the FigCraft fixtures before using its player for an end-to-end demo. |
| High | Data is only in browser memory. Refreshing loses a user's draft and all created records. | Observe whether participants refresh or close the tab; define persistence before building the app. |
| High | The public catalogue is simulated. Link expiry, per-shop access, and real LINE communication are not implemented. | Test the language and layout only; design authenticated sharing and expired-link recovery in the app phase. |
| Medium | Mobile keyboard, safe area, long lists, and scroll behavior have not been visually verified on multiple devices. | Test the hosted build on real iOS and Android phones, especially bill, reservation, and receiving forms. |
| Medium | Model setup still offers fixed size/color/pack choices in the web prototype. | Validate actual catalogues from more clothing shops, then allow shop-specific values if needed. |
| Medium | Assistant restrictions are demonstrated by a role switch in the prototype, without server authorization. | Validate role language with users; enforce permissions on the backend. |

Completed in the current design: the store bottom menu is linked on 30 FigCraft screens; receiving and reservation edit/cancel paths have distinct outcomes; the web prototype retains in-progress tabs and updates stock/reserved totals when those records change. See `docs/flow-transitions.md` and the smoke checks for the exact transitions.
