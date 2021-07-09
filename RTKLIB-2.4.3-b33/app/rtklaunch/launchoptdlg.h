//---------------------------------------------------------------------------

#ifndef launchoptdlgH
#define launchoptdlgH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>
//---------------------------------------------------------------------------
class TLaunchOptDialog : public TForm
{
__published:	// IDE �ŊǗ������R���|�[�l���g
	TRadioButton *OptMkl;
	TRadioButton *OptWin64;
	TButton *BtnCancel;
	TButton *BtnOk;
	TRadioButton *OptNormal;
	TCheckBox *Minimize;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall BtnOkClick(TObject *Sender);
private:	// ���[�U�[�錾
public:		// ���[�U�[�錾
	__fastcall TLaunchOptDialog(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TLaunchOptDialog *LaunchOptDialog;
//---------------------------------------------------------------------------
#endif
