import React from 'react';
import { instrumentCatalogFixture } from '../data/instrumentCatalogFixture';
import './InstrumentCatalogPanel.css';

const InstrumentCatalogPanel: React.FC = () => (
  <section className="instrument-catalog" aria-labelledby="instrument-catalog-title">
    <div className="instrument-catalog__heading">
      <div>
        <p className="instrument-catalog__eyebrow">INSTRUMENT METADATA</p>
        <h2 id="instrument-catalog-title">Supported products</h2>
      </div>
      <span className="instrument-catalog__status">OFFLINE FIXTURE</span>
    </div>

    <p className="instrument-catalog__note">{instrumentCatalogFixture.note}</p>

    <div className="instrument-catalog__list">
      {instrumentCatalogFixture.supportedProducts.map((product) => (
        <article className="instrument-catalog__item" key={product.root}>
          <div className="instrument-catalog__symbol">{product.root}</div>
          <div className="instrument-catalog__details">
            <strong>{product.productName}</strong>
            <span>{product.dataset} · Root supported, expiry definitions not loaded</span>
          </div>
          <span className="instrument-catalog__count">0 contracts</span>
        </article>
      ))}
    </div>

    <p className="instrument-catalog__footnote">
      No active contract is selected automatically. Contract listings will appear only
      after verified instrument definitions become available.
    </p>
  </section>
);

export default InstrumentCatalogPanel;
