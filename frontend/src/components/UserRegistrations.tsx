import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { UserRegistration, RegistrationFilter, ApprovalRequest } from '../types/admin';
import { adminApi } from '../services/adminApi';
import { CheckCircle, XCircle, Clock, User, Wallet, Building2, Calendar } from 'lucide-react';
import { toast } from 'sonner';

interface UserRegistrationsProps {
  onStatsUpdate?: () => void;
}

export const UserRegistrations = ({ onStatsUpdate }: UserRegistrationsProps) => {
  const [registrations, setRegistrations] = useState<UserRegistration[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<RegistrationFilter>('all');
  const [selectedUser, setSelectedUser] = useState<UserRegistration | null>(null);
  const [showApprovalDialog, setShowApprovalDialog] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');
  const [processing, setProcessing] = useState(false);

  // Load registrations
  const loadRegistrations = async (statusFilter: RegistrationFilter = filter) => {
    setLoading(true);
    const response = await adminApi.getRegistrations({
      status: statusFilter,
      limit: 100,
    });

    if (response.success && response.data) {
      setRegistrations(response.data);
    } else {
      toast.error(`Errore nel caricamento delle registrazioni: ${response.error}`);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadRegistrations(filter);
  }, [filter]);

  // Handle approval
  const handleApproval = async () => {
    if (!selectedUser) return;

    setProcessing(true);
    const request: ApprovalRequest = {
      user_id: selectedUser.id,
      approval_notes: approvalNotes.trim() || undefined,
    };

    const response = await adminApi.approveRegistration(request);
    
    if (response.success) {
      toast.success(`Utente ${selectedUser.username} approvato con successo`);
      setShowApprovalDialog(false);
      setSelectedUser(null);
      setApprovalNotes('');
      await loadRegistrations();
      onStatsUpdate?.();
    } else {
      toast.error(`Errore nell'approvazione: ${response.error}`);
    }
    setProcessing(false);
  };

  // Handle rejection
  const handleRejection = async (user: UserRegistration) => {
    if (!confirm(`Sei sicuro di voler rifiutare la registrazione di ${user.username}?`)) {
      return;
    }

    setProcessing(true);
    const response = await adminApi.rejectRegistration(user.id, 'Registrazione rifiutata dall\'amministratore');
    
    if (response.success) {
      toast.success(`Utente ${user.username} rifiutato`);
      await loadRegistrations();
      onStatsUpdate?.();
    } else {
      toast.error(`Errore nel rifiuto: ${response.error}`);
    }
    setProcessing(false);
  };

  // Status badge component
  const StatusBadge = ({ status }: { status: UserRegistration['status'] }) => {
    const variants = {
      pending: { variant: 'secondary' as const, icon: Clock, color: 'text-yellow-600' },
      approved: { variant: 'secondary' as const, icon: CheckCircle, color: 'text-green-600' },
      rejected: { variant: 'destructive' as const, icon: XCircle, color: 'text-red-600' },
    };

    const { variant, icon: Icon, color } = variants[status];
    
    return (
      <Badge variant={variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${color}`} />
        {status === 'pending' ? 'In attesa' : status === 'approved' ? 'Approvato' : 'Rifiutato'}
      </Badge>
    );
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Filter buttons
  const filterButtons: { value: RegistrationFilter; label: string; count: number }[] = [
    { value: 'all', label: 'Tutte', count: Array.isArray(registrations) ? registrations.length : 0 },
    { value: 'pending', label: 'In attesa', count: Array.isArray(registrations) ? registrations.filter(r => r.status === 'pending').length : 0 },
    { value: 'approved', label: 'Approvate', count: Array.isArray(registrations) ? registrations.filter(r => r.status === 'approved').length : 0 },
    { value: 'rejected', label: 'Rifiutate', count: Array.isArray(registrations) ? registrations.filter(r => r.status === 'rejected').length : 0 },
  ];

  const filteredRegistrations = filter === 'all' 
    ? (Array.isArray(registrations) ? registrations : [])
    : (Array.isArray(registrations) ? registrations.filter(r => r.status === filter) : []);

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Registrazioni Utenti
          </CardTitle>
          <CardDescription>
            Gestisci le richieste di registrazione degli utenti
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filter buttons */}
          <div className="flex flex-wrap gap-2 mb-6">
            {filterButtons.map((btn) => (
              <Button
                key={btn.value}
                variant={filter === btn.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(btn.value)}
                disabled={loading}
              >
                {btn.label} ({btn.count})
              </Button>
            ))}
          </div>

          {/* Table */}
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-2">Caricamento...</span>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Utente</TableHead>
                    <TableHead>Wallet</TableHead>
                    <TableHead>DEX Preferito</TableHead>
                    <TableHead>Data Registrazione</TableHead>
                    <TableHead>Stato</TableHead>
                    <TableHead>Azioni</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRegistrations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                        Nessuna registrazione trovata
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredRegistrations.map((registration) => (
                      <TableRow key={registration.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            {registration.username}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Wallet className="h-4 w-4 text-muted-foreground" />
                            <code className="text-sm">
                              {registration.wallet_address.slice(0, 6)}...
                              {registration.wallet_address.slice(-4)}
                            </code>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Building2 className="h-4 w-4 text-muted-foreground" />
                            {registration.preferred_dex}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            {formatDate(registration.registration_date)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <StatusBadge status={registration.status} />
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            {registration.status === 'pending' && (
                              <>
                                <Button
                                  size="sm"
                                  onClick={() => {
                                    setSelectedUser(registration);
                                    setShowApprovalDialog(true);
                                  }}
                                  disabled={processing}
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Approva
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleRejection(registration)}
                                  disabled={processing}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Rifiuta
                                </Button>
                              </>
                            )}
                            {registration.status === 'approved' && registration.approved_by && (
                              <div className="text-xs text-muted-foreground">
                                Approvato da {registration.approved_by}
                                {registration.approved_at && (
                                  <div>{formatDate(registration.approved_at)}</div>
                                )}
                              </div>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Approval Dialog */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approva Registrazione</DialogTitle>
            <DialogDescription>
              Stai approvando la registrazione di <strong>{selectedUser?.username}</strong>.
              Puoi aggiungere delle note opzionali.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="approval-notes">Note di approvazione (opzionali)</Label>
              <Textarea
                id="approval-notes"
                placeholder="Aggiungi eventuali note sulla approvazione..."
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                rows={3}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowApprovalDialog(false);
                setApprovalNotes('');
                setSelectedUser(null);
              }}
              disabled={processing}
            >
              Annulla
            </Button>
            <Button
              onClick={handleApproval}
              disabled={processing}
            >
              {processing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Approvando...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approva
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};