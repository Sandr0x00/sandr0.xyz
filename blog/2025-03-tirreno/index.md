## tirreno - how to respectfully treat researchers

2025-03-15<br/>
by [Sandro Bauer](https://sandr0.xyz)

While being bored one day in January, I searched GitHub for some fun projects to look at and randomly stumbled on tirreno[^tirreno-github].

After playing around with it, it became clear that data sent to the platform is not properly sanitized and XSS is possible in some fields.

For example, it was possible to send `<script>alert(1)//` as `userName` or `url` to cause an alert window to pop up in Dashboard, Users, Resources, ... indicating that I was able to execute JavaScript code.

Thanks to using `&ellip;`, proper payloads demand more crafting.

Following the `README.md`[^readme] in the repository, I reported this finding to [security@tirreno.com](mailto:security@tirreno.com) and they properly fixed it the same day[^fix] and released a new version properly crediting me, the security researcher[^release].

On top of all that, Alex from tirreno offered me some company swag as a token of gratitude, which I thankfully accepted leading to us meeting at Insomni'hack[^insomnihack] in Lausanne (where tirreno is located) and having an interesting talk.

I want to thank Alex and the tirreno team for their awesome work, these people are in it with all their heart and you can see it by looking at the project.

In my opinion, this is what security research should be about. Working together, making the world a little bit better, forming connections and having fun hacking.

[^readme]: <https://github.com/TirrenoTechnologies/tirreno?tab=readme-ov-file#reporting-a-security-issue>
[^tirreno-github]: <https://github.com/TirrenoTechnologies/tirreno>
[^release]: <https://github.com/TirrenoTechnologies/tirreno/releases/tag/v0.9.2>
[^fix]: <https://github.com/TirrenoTechnologies/tirreno/commit/b9bfa224234a405aa2a0c8275611edeba4183a1b>
[^insomnihack]: <https://insomnihack.ch>
