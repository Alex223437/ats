import { useEffect, useRef } from 'react';
import './ConfirmModal.scss';

const ConfirmModal = ({ isOpen, title, message, onConfirm, onCancel, loading }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        onCancel(); // Закрываем при клике вне модалки
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content" ref={modalRef}>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="cancel-btn" onClick={onCancel} disabled={loading}>
            Cancel
          </button>
          <button className="confirm-btn" onClick={onConfirm} disabled={loading}>
            {loading ? 'Disconnecting...' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;