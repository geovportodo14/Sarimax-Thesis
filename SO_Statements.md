## Student Outcome Statements

**Project:** SARIMAX-Based Monitoring System for Household Appliance Energy Forecasting
**Contributor:** Geovanny V. Portodo — Lead / Full-Stack Developer
**Program:** Bachelor of Science in Computer Science, Technological Institute of the Philippines
**Adviser:** Dr. Melvin Ballera

---

### SO1 — Analyze a complex computing problem and apply principles of computing and other relevant disciplines to identify solutions.

I served as the lead developer of a household energy forecasting system that combined Internet of Things data ingestion, time-series statistics, and operations research into a single working pipeline that ran end-to-end against live data. The problem itself was layered, as raw ten-minute Tuya smart plug readings had to be cleaned, hourly aggregated, and merged with weather exogenous variables before a SARIMAX model could produce meaningful forecasts, and even then, a forecast alone did not yet answer the user’s real question of how to remain within a Meralco budget for the month.

I decomposed the problem into measurable sub-problems and addressed each one with the appropriate discipline, applying statistical modeling for the forecasting layer, mixed-integer linear programming for the appliance scheduling layer, and software engineering for the orchestration that connected them. This decomposition was not done once and forgotten, but revisited at every milestone whenever a new constraint, such as an API quota or a data gap, forced me to redraw the boundary between layers.

When my first feature configuration treated atmospheric pressure as an exogenous regressor and failed to improve accuracy, I analyzed the residuals, replaced the variable with rainfall, and re-evaluated the model against the MAPE less-than-or-equal-to five percent and R-squared greater-than-or-equal-to zero point seven targets defined in the thesis. The substitution was decided strictly on the residual evidence from our own dataset, rather than on the strength of any prior study.

That decomposition, which required me to diagnose whether each weakness was a data problem, a model problem, or an integration problem before attempting a fix, is the analytical work that this outcome calls for.

---

### SO2 — Design, implement, and evaluate a computing-based solution to meet a given set of computing requirements in the context of the program’s discipline.

I designed and implemented the full stack of the system, from the data collector through to the user interface, and then evaluated it across repeated iteration cycles in preparation for the thesis defense. The work spans roughly three months of continuous development and is reflected in more than eighty commits authored under my account on the main branch of this repository.

On the back end, I built the continuous Tuya collector with a smart-backfill safety net that protects against missing intervals after an outage, the four-stage preprocessing pipeline that produces the modeling-ready datasets in the project’s data directory, the FastAPI forecasting service that serves the trained SARIMAX models, and the mixed-integer linear programming scheduler that emits the daily recommendation and schedule artifacts.

On the front end, I implemented the React dashboard and its supporting components, including the landing page, the dashboard page, the actual-versus-forecast chart, the smart budget card, the billing cycle card, and the forecast generator card, so that a non-technical user could meaningfully consume the model output without needing to read a single line of code.

To satisfy evaluation requirements, I authored dedicated harnesses for back-testing the model against baselines, for batch evaluation across multiple run dates, and for budget stress testing under different consumption scenarios, and I iterated the model through four major versions until the accuracy targets defined in the research objectives were met.

The culminating implementation effort, which simultaneously refactored the forecasting pipeline to version two and migrated the optimization solver to a binary CBC build, integrated approximately four thousand four hundred lines of new code across forty-three files in a single coordinated release.

---

### SO3 — Communicate effectively in a variety of professional contexts.

I treated documentation as a first-class deliverable rather than as an artifact produced after the code was finished, and the repository now contains a written companion for every major decision the system makes.

The project README explains the separation-of-concerns architecture so that a reader can understand why the data collector runs on an Azure virtual machine while preprocessing runs locally on a development machine, and a dedicated MILP explainer translates the optimization layer into plain English using cost meters, hourly timelines, and a thesis-ready process diagram for non-mathematical readers.

For the team and the adviser, I prepared the consolidated thesis core document, a system analysis document, an implementation defense preparation document, and a fully timed defense flow, all of which we used to rehearse the panel presentation in the weeks leading up to it.

When I planned the Meralco billing-cycle widget, I authored an implementation plan that specified the data model, the projection logic, the status computation, the relevant edge cases, and the output contract returned to the user interface before any code was written, and only afterward shipped the corresponding React component.

Communicating the rationale before the implementation is what allowed teammates and the adviser to review intent rather than only code, and it is what made each review session productive instead of speculative.

---

### SO4 — Recognize professional responsibilities and make informed judgments in computing practice based on legal and ethical principles.

Working on a system that handles a real household’s energy data required me to take privacy, accuracy, and honesty seriously throughout the project, even when shortcuts would have been faster.

Early in development, I identified and removed Tuya API credentials that had been committed to the repository, then relocated all secrets into a local environment file and the Docker environment so that the project could be shared without exposing live access to Internet of Things devices in someone’s home.

When I discovered that the voltage feature was running on a placeholder constant rather than measured values, I replaced it with the actual readings rather than allow the model to present synthetic numbers as real measurements, even though doing so meant revisiting weeks of earlier results.

After the adviser raised concerns about claims the dashboard implicitly made to end users, I added a forecast disclaimer to the user interface so that consumers understand that the SARIMAX outputs are statistical predictions rather than guarantees of future cost, and updated the surrounding copy to match.

Each of those decisions was a small judgment call, and taken together, they shaped the way I now think about the professional responsibility that a developer carries when software is placed in front of a real person.

---

### SO5 — Function effectively as a member or leader of a team engaged in activities appropriate to the program’s discipline.

Although I held the lead developer role across the entire project, the thesis was a three-person collaboration with Jhona Lyn Suaverdez and John Raphael Laxa, and nearly every meaningful change began with a team discussion or an adviser note rather than with a unilateral decision of mine.

I integrated Suaverdez’s feedback on the system flow and the optimization rules directly into the implementation, restructuring the user-facing workflow and revising the MILP formulation in successive iterations until it matched the agreed design rather than only my initial preference.

I incorporated Dr. Ballera’s and Doc Apo’s panel feedback the same way, most notably by adding the forecast disclaimer requested during a review and by adjusting the cost estimation methodology to reflect their guidance.

When my teammate Laxa contributed credential updates to the collector, I coordinated my subsequent backfill and Docker changes around his work so that the deployment remained consistent rather than overwriting his contribution and forcing him to reapply it.

My role on the team was therefore not measured only by the volume of code I produced, but by my consistency in taking the group’s decisions and the adviser’s critiques and converting them into a working system in time for the next milestone.

---

### SO6 — Apply computer science theory and software development fundamentals to produce computing-based solutions.

The forecasting and optimization layers of this thesis are direct applications of computer science theory that I learned across the program, and the surrounding system is a direct application of software engineering practice.

The SARIMAX model required me to apply time-series concepts such as stationarity testing, seasonal differencing, autoregressive and moving-average parameterization, and the careful selection of exogenous regressors, all of which were validated against the quantitative accuracy targets defined in the research objectives rather than accepted on intuition alone.

The appliance scheduling layer applies mixed-integer linear programming, in which I represented the on and off state of each appliance for each hour as a binary decision variable, enforced the household budget as a linear constraint, and solved the resulting model using a binary CBC solver that produces the daily recommendation and schedule artifacts consumed by the front end.

Around these theoretical layers, I applied software development fundamentals as well, including a separation-of-concerns architecture between the data collector and the preprocessing pipeline, containerization with Docker for reproducible deployment to an Azure virtual machine, a clearly typed contract between the FastAPI service and the React user interface, and version control discipline that allowed me to maintain four parallel SARIMAX iterations without losing earlier work.

Taken together, these layers demonstrate that the system is not only an engineering artifact, but also a working application of the theory that has been taught throughout the program, executed under real-world constraints rather than in a controlled laboratory setting.

---

## Reflection on the Student Outcomes

Working through these six outcomes taught me that analyzing a complex computing problem is far less about producing a clever solution on the first attempt, and far more about being willing to take the problem apart again every time the evidence pushes back. Once I forced myself to diagnose whether each weakness was a data problem, a model problem, or an integration problem before attempting any fix, the work finally became tractable, and I began making design decisions that I could defend in front of the panel rather than only justify after the fact. The same discipline applied to the engineering side, because each version of the system that I had once considered complete eventually revealed a constraint that I had not yet accounted for, and evaluating my own work honestly, rather than only celebrating that it ran at all, was the change in mindset that allowed each version to become genuinely better than the last.

I entered this thesis believing that strong code could substitute for strong communication, and I left it convinced of exactly the opposite, because the work that survived review was not necessarily the most elegantly written, but the work that I could explain clearly to a teammate, to the adviser, and to a panel of strangers. Writing implementation plans before the code, and writing the MILP explainer in plain English instead of mathematical notation, forced me to confront the gaps in my own understanding before anyone else had the chance to. The professional responsibility that runs alongside that communication also became personal rather than abstract during this project, since I learned that ethics in software is rarely a single dramatic decision and is far more often a series of small judgment calls made under time pressure, such as whether to display a placeholder, whether to commit a credential, or whether to caveat a forecast that a user might act on.

Being the most active contributor on a small team taught me that leadership is not about producing the largest number of commits, but about preserving the team’s ability to keep moving together, and the moments I am most proud of are not the ones in which I wrote the most code, but the ones in which I revised a working component because a teammate or the adviser had a clearer understanding of what the user actually needed. Underneath all of this, the project finally made me appreciate how much of my undergraduate coursework had been preparing me for a single moment of integration, in which statistics, optimization, software engineering, and systems work all had to operate against the same real measurements at the same time. Going forward, I will no longer treat theory and engineering, or code and communication, or individual ownership and team responsibility, as separate categories, because this project showed me that a strong solution requires all of them, applied together, by the same person.
