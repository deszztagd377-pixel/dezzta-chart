import React, { useEffect, useMemo, useState } from 'react';
import type { FuturesContractDto, InstrumentRoot } from '../types/instrumentCatalogApi';
import { fetchInstrumentCatalog, InstrumentCatalogError } from '../services/instrumentCatalogClient';
import './InstrumentCatalogPanel.css';

type CatalogStatus = 'loading' | 'ready' | 'empty' | 'error';

interface InstrumentCatalogPanelProps {
  apiBaseUrl: string;
  selectedContract: FuturesContractDto | null;
  onSelectContract: (contract: FuturesContractDto) => void;
  onClearSelection: () => void;
}

const ROOTS: InstrumentRoot[] = ['ES', 'NQ', 'GC'];

const InstrumentCatalogPanel: React.FC<InstrumentCatalogPanelProps> = ({
  apiBaseUrl,
  selectedContract,
  onSelectContract,
  onClearSelection,
}) => {
  const [root, setRoot] = useState<InstrumentRoot>('ES');
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<CatalogStatus>('loading');
  const [contracts, setContracts] = useState<FuturesContractDto[]>([]);
  const [productName, setProductName] = useState('E-mini S&P 500 Futures');
  const [errorMessage, setErrorMessage] = useState('');
  const [refreshNonce, setRefreshNonce] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setStatus('loading');
    setErrorMessage('');
    setContracts([]);

    fetchInstrumentCatalog({ baseUrl: apiBaseUrl, root, signal: controller.signal })
      .then((catalog) => {
        setContracts(catalog.contracts);
        setProductName(catalog.supported_products.find((item) => item.root === root)?.product_name ?? root);
        setStatus(catalog.contract_count > 0 ? 'ready' : 'empty');
      })
      .catch((error: unknown) => {
        if (error instanceof InstrumentCatalogError && error.code === 'cancelled') return;
        setContracts([]);
        setStatus('error');
        setErrorMessage(error instanceof Error ? error.message : 'Unable to load instrument catalog.');
      });

    return () => controller.abort();
  }, [apiBaseUrl, root, refreshNonce]);

  const visibleContracts = useMemo(() => {
    const query = search.trim().toUpperCase();
    if (!query) return contracts;
    return contracts.filter((contract) =>
      contract.raw_symbol.includes(query) ||
      contract.expiration.includes(query) ||
      String(contract.instrument_id).includes(query),
    );
  }, [contracts, search]);

  const isSelected = (contract: FuturesContractDto) =>
    selectedContract?.dataset === contract.dataset &&
    selectedContract.publisher_id === contract.publisher_id &&
    selectedContract.instrument_id === contract.instrument_id;

  return (
    <section className="instrument-catalog" aria-labelledby="instrument-catalog-title">
      <div className="instrument-catalog__heading">
        <div>
          <p className="instrument-catalog__eyebrow">VERIFIED INSTRUMENT CATALOG</p>
          <h2 id="instrument-catalog-title">Select contract</h2>
        </div>
        <span className={`instrument-catalog__status instrument-catalog__status--${status}`}>
          {status === 'loading' ? 'LOADING' : status === 'ready' ? 'CATALOG READY' : status === 'empty' ? 'NO DEFINITIONS' : 'API UNAVAILABLE'}
        </span>
      </div>

      <div className="instrument-catalog__root-tabs" role="group" aria-label="Filter futures product">
        {ROOTS.map((item) => (
          <button
            type="button"
            key={item}
            className={root === item ? 'is-active' : ''}
            aria-pressed={root === item}
            onClick={() => { setRoot(item); setSearch(''); }}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="instrument-catalog__product-line">
        <strong>{productName}</strong>
        <span>{contracts.length} verified contract{contracts.length === 1 ? '' : 's'}</span>
      </div>

      {selectedContract && (
        <div className="instrument-catalog__selection" role="status">
          <div>
            <span className="instrument-catalog__selection-label">SELECTED METADATA</span>
            <strong>{selectedContract.raw_symbol}</strong>
            <small>{selectedContract.expiration} · ID {selectedContract.instrument_id}</small>
          </div>
          <button type="button" onClick={onClearSelection}>Clear</button>
        </div>
      )}

      <label className="instrument-catalog__search">
        <span>Search symbol, expiry, or instrument ID</span>
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="e.g. ESZ6"
          disabled={status !== 'ready'}
        />
      </label>

      {status === 'loading' && (
        <div className="instrument-catalog__message" role="status">
          <span className="instrument-catalog__spinner" />
          Loading verified {root} contracts…
        </div>
      )}

      {status === 'error' && (
        <div className="instrument-catalog__message instrument-catalog__message--error" role="alert">
          <strong>Catalog could not be loaded</strong>
          <span>{errorMessage}</span>
          <button type="button" onClick={() => setRefreshNonce((value) => value + 1)}>Retry</button>
        </div>
      )}

      {status === 'empty' && (
        <div className="instrument-catalog__message">
          <strong>No verified {root} contracts are available.</strong>
          <span>The backend returned an empty catalog. No expiry or active contract has been invented.</span>
        </div>
      )}

      {status === 'ready' && visibleContracts.length === 0 && (
        <div className="instrument-catalog__message">
          No contracts match “{search}”.
        </div>
      )}

      {status === 'ready' && visibleContracts.length > 0 && (
        <div className="instrument-catalog__list" aria-live="polite">
          {visibleContracts.map((contract) => (
            <button
              type="button"
              className={`instrument-catalog__item ${isSelected(contract) ? 'is-selected' : ''}`}
              key={`${contract.dataset}:${contract.publisher_id}:${contract.instrument_id}`}
              onClick={() => onSelectContract(contract)}
              aria-pressed={isSelected(contract)}
            >
              <span className="instrument-catalog__symbol">{contract.root}</span>
              <span className="instrument-catalog__details">
                <strong>{contract.raw_symbol}</strong>
                <span>Expires {contract.expiration} · {contract.currency ?? 'Currency n/a'}</span>
                <span>Min tick {contract.min_price_increment ?? 'n/a'} · ID {contract.instrument_id}</span>
              </span>
              <span className="instrument-catalog__choose">{isSelected(contract) ? 'SELECTED' : 'SELECT'}</span>
            </button>
          ))}
        </div>
      )}

      <div className="instrument-catalog__footnote">
        Contract selection uses verified backend definitions only. Selection stores metadata; it does not imply that OHLCV data is available or that the chart has switched from DEMO.
      </div>
    </section>
  );
};

export default InstrumentCatalogPanel;
