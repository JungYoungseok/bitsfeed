"use client";

//import { useEffect } from "react";
import { datadogRum } from '@datadog/browser-rum';
//import { reactPlugin } from '@datadog/browser-rum-react';

export function DatadogRUM() {

  datadogRum.init({
    applicationId: '57bf6486-cd46-430c-aacd-0b16764c78ba',
    clientToken: 'pub29626c776ade9f7b38b80464fe9a56a7',
    site: 'datadoghq.com',
    service: 'news-frontend',
    env: 'prod',
    version: '1.0.0',
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    defaultPrivacyLevel: 'allow',
  });


    // datadogRum.init({
    //   applicationId: process.env.NEXT_PUBLIC_DD_RUM_APP_ID!,
    //   clientToken: process.env.NEXT_PUBLIC_DD_RUM_CLIENT_TOKEN!,
    //   site: (process.env.NEXT_PUBLIC_DD_RUM_SITE as "datadoghq.com") || "datadoghq.com",
     
    //   service:'datadog-news-front',
    //   env: 'prod',
    //   version: "1.0.0",
    //   sessionSampleRate: 100,
    //   sessionReplaySampleRate: 100,
    //   defaultPrivacyLevel: 'allow',
    //   plugins: [reactPlugin({ router: true })],
    // });

    
    // no-dd-sa
    console.log("🔥 Datadog RUM initialized");
    return null;
}
