"use client";

import { useEffect } from "react";
import { datadogRum } from '@datadog/browser-rum';
import { reactPlugin } from '@datadog/browser-rum-react';

export function DatadogRUM() {
  useEffect(() => {
    datadogRum.init({
      applicationId: process.env.NEXT_PUBLIC_DD_RUM_APP_ID!,
      clientToken: process.env.NEXT_PUBLIC_DD_RUM_CLIENT_TOKEN!,
      site: (process.env.NEXT_PUBLIC_DD_RUM_SITE as "datadoghq.com") || "datadoghq.com",
     
      service:'datadog-news-front',
      env: 'prod',
      version: "1.0.0",
      sessionSampleRate: 100,
      sessionReplaySampleRate: 100,
      defaultPrivacyLevel: 'allow',
      plugins: [reactPlugin({ router: true })],
    });
    console.log("🔥 Datadog RUM initialized");
  }, []);

  return null;
}
