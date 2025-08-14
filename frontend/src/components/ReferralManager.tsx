import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { ReferralLink } from '../types/admin';
import { adminApi } from '../services/adminApi';
import { Link, Plus, Edit, Trash2, ExternalLink, MousePointer, Users, Calendar } from 'lucide-react';
import { toast } from 'sonner';

export const ReferralManager = () => {
  const [referralLinks, setReferralLinks] = useState<ReferralLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingLink, setEditingLink] = useState<ReferralLink | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    is_active: true,
  });
  const [processing, setProcessing] = useState(false);

  // Load referral links
  const loadReferralLinks = async () => {
    setLoading(true);
    const response = await adminApi.getReferralLinks();

    if (response.success && response.data) {
      setReferralLinks(response.data);
    } else {
      toast.error(`Errore nel caricamento dei link di referral: ${response.error}`);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadReferralLinks();
  }, []);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.url.trim()) {
      toast.error('Nome e URL sono obbligatori');
      return;
    }

    // Basic URL validation
    try {
      new URL(formData.url);
    } catch {
      toast.error('URL non valido');
      return;
    }

    setProcessing(true);

    try {
      if (editingLink) {
        // Update existing link
        const response = await adminApi.updateReferralLink(editingLink.id, {
          name: formData.name.trim(),
          url: formData.url.trim(),
          is_active: formData.is_active,
        });

        if (response.success) {
          toast.success('Link di referral aggiornato con successo');
          await loadReferralLinks();
          handleCloseDialog();
        } else {
          toast.error(`Errore nell'aggiornamento: ${response.error}`);
        }
      } else {
        // Create new link
        const response = await adminApi.createReferralLink(
          formData.name.trim(),
          formData.url.trim()
        );

        if (response.success) {
          toast.success('Link di referral creato con successo');
          await loadReferralLinks();
          handleCloseDialog();
        } else {
          toast.error(`Errore nella creazione: ${response.error}`);
        }
      }
    } catch (error) {
      toast.error('Errore imprevisto');
      console.error('Error:', error);
    }

    setProcessing(false);
  };

  // Handle delete
  const handleDelete = async (link: ReferralLink) => {
    if (!confirm(`Sei sicuro di voler eliminare il link "${link.name}"?`)) {
      return;
    }

    setProcessing(true);
    const response = await adminApi.deleteReferralLink(link.id);
    
    if (response.success) {
      toast.success('Link di referral eliminato');
      await loadReferralLinks();
    } else {
      toast.error(`Errore nell'eliminazione: ${response.error}`);
    }
    setProcessing(false);
  };

  // Handle edit
  const handleEdit = (link: ReferralLink) => {
    setEditingLink(link);
    setFormData({
      name: link.name,
      url: link.url,
      is_active: link.is_active,
    });
    setShowDialog(true);
  };

  // Handle dialog close
  const handleCloseDialog = () => {
    setShowDialog(false);
    setEditingLink(null);
    setFormData({
      name: '',
      url: '',
      is_active: true,
    });
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

  // Status badge
  const StatusBadge = ({ isActive }: { isActive: boolean }) => (
    <Badge variant={isActive ? 'secondary' : 'outline'} className="flex items-center gap-1">
      <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-500' : 'bg-gray-400'}`} />
      {isActive ? 'Attivo' : 'Inattivo'}
    </Badge>
  );

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Link className="h-5 w-5" />
                Gestione Link di Referral
              </CardTitle>
              <CardDescription>
                Crea e gestisci i link di referral per le campagne di marketing
              </CardDescription>
            </div>
            <Button onClick={() => setShowDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nuovo Link
            </Button>
          </div>
        </CardHeader>
        <CardContent>
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
                    <TableHead>Nome</TableHead>
                    <TableHead>URL</TableHead>
                    <TableHead>Click</TableHead>
                    <TableHead>Registrazioni</TableHead>
                    <TableHead>Stato</TableHead>
                    <TableHead>Creato</TableHead>
                    <TableHead>Azioni</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {referralLinks.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        Nessun link di referral trovato
                      </TableCell>
                    </TableRow>
                  ) : (
                    referralLinks.map((link) => (
                      <TableRow key={link.id}>
                        <TableCell className="font-medium">
                          {link.name}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2 max-w-xs">
                            <code className="text-sm truncate bg-muted px-2 py-1 rounded">
                              {link.url}
                            </code>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => window.open(link.url, '_blank')}
                              className="flex-shrink-0"
                            >
                              <ExternalLink className="h-3 w-3" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <MousePointer className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">{link.clicks}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">{link.registrations}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <StatusBadge isActive={link.is_active} />
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">{formatDate(link.created_at)}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(link)}
                              disabled={processing}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDelete(link)}
                              disabled={processing}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
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

      {/* Create/Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={(open) => !open && handleCloseDialog()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingLink ? 'Modifica Link di Referral' : 'Nuovo Link di Referral'}
            </DialogTitle>
            <DialogDescription>
              {editingLink 
                ? 'Modifica i dettagli del link di referral' 
                : 'Crea un nuovo link di referral per le tue campagne'
              }
            </DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="name">Nome *</Label>
              <Input
                id="name"
                placeholder="es. Campagna Social Media"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </div>

            <div>
              <Label htmlFor="url">URL *</Label>
              <Input
                id="url"
                type="url"
                placeholder="https://esempio.com/referral"
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                required
              />
            </div>

            <div className="flex items-center space-x-2">
              <Switch
                id="is_active"
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))}
              />
              <Label htmlFor="is_active">Link attivo</Label>
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleCloseDialog}
                disabled={processing}
              >
                Annulla
              </Button>
              <Button
                type="submit"
                disabled={processing}
              >
                {processing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {editingLink ? 'Aggiornando...' : 'Creando...'}
                  </>
                ) : (
                  <>
                    {editingLink ? (
                      <>
                        <Edit className="h-4 w-4 mr-2" />
                        Aggiorna
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-2" />
                        Crea
                      </>
                    )}
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
};