import { describe, expect, it } from "vitest";

import { beforeSend, cleanAddress } from "./audience";

describe("cleanAddress", () => {
  it("retire les jetons des liens envoyés par email", () => {
    expect(cleanAddress("https://ximaths.fr/mot-de-passe/nouveau?uid=MQ&token=abc-123")).toBe(
      "https://ximaths.fr/mot-de-passe/nouveau",
    );
    expect(cleanAddress("/verifier-email?academique=xyz")).toBe("/verifier-email");
  });

  it("retire le jeton de la page d'envoi des photos", () => {
    expect(cleanAddress("https://ximaths.fr/photos/Zk3_9aQ")).toBe("https://ximaths.fr/photos/");
    expect(cleanAddress("/photos/Zk3_9aQ")).toBe("/photos/");
  });

  it("garde les paramètres de campagne et le reste de l'adresse", () => {
    expect(cleanAddress("https://ximaths.fr/defi?utm_source=discord&ref=x#haut")).toBe(
      "https://ximaths.fr/defi?utm_source=discord",
    );
    expect(cleanAddress("https://www.google.com/")).toBe("https://www.google.com/");
    expect(cleanAddress("/exercices/12")).toBe("/exercices/12");
  });

  it("laisse passer une adresse vide", () => {
    expect(cleanAddress("")).toBe("");
    expect(cleanAddress(undefined)).toBeUndefined();
  });
});

describe("beforeSend", () => {
  it("nettoie l'adresse et la provenance, sans toucher au reste", () => {
    expect(
      beforeSend("event", {
        website: "id",
        url: "https://ximaths.fr/verifier-email?token=abc",
        referrer: "/photos/tok",
        title: "XiMaths",
      }),
    ).toEqual({ website: "id", url: "https://ximaths.fr/verifier-email", referrer: "/photos/", title: "XiMaths" });
  });
});
